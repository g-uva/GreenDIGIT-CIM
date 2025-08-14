from fastapi import FastAPI, Depends, HTTPException, status, Request, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
import time
import os
from dotenv import load_dotenv
from metrics_store import store_metric, _col
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, Session

load_dotenv()  # loads from .env in the current folder by default

tags_metadata = [
    {
        "name": "Auth",
        "description": "Login to obtain a JWT Bearer token. Use this token in `Authorization: Bearer <token>` on all protected endpoints.",
    },
    {
        "name": "Metrics",
        "description": "Submit and list metrics. **Requires** `Authorization: Bearer <token>`.",
    },
]

app = FastAPI(
    title="GreenDIGIT WP6.2 CIM Metrics API",
    description=(
        "API for publishing metrics.\n\n"
        "**Authentication**\n\n"
        "- Obtain a token via **POST /login** using form fields `email` and `password`. Your email must be registered beforehand. In case this does not work (wrong password/unknown), please contact goncalo.ferreira@student.uva.nl or a.tahir2@uva.nl.\n"
        "- Then include `Authorization: Bearer <token>` on all protected requests.\n"
        "- Tokens expire after 1 day—in which case you must simply repeat the process again.\n"
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"persistAuthorization": True},
    root_path="/gd-cim-api"
)
security = HTTPBearer()

# Secret key for JWT
SECRET_KEY = os.environ["JWT_TOKEN"]
if not SECRET_KEY:
    raise RuntimeError("JWT_TOKEN not valid. You must generate a valid token on the server. :)")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400 # 1 day
JWT_ISSUER = os.environ.get("JWT_ISSUER", "greendigit-login-uva")

# SQLite setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SubmitData(BaseModel):
    field1: str
    field2: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_allowed_emails():
    path = os.path.join(os.path.dirname(__file__), "allowed_emails.txt")
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return set(line.strip().lower() for line in f if line.strip())

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp", "iat", "nbf", "iss"]},
            issuer=JWT_ISSUER
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post(
    "/login",
    tags=["Auth"],
    summary="Login and get a JWT access token",
    description=(
        "Use form fields `username` (email) and `password`.\n\n"
        "Returns a JWT for `Authorization: Bearer <token>`."
    )
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email_lower = form_data.username.strip().lower()
    user = db.query(User).filter(User.email == email_lower).first()
    if not user:
        # First login: check if allowed, then register
        allowed_emails = load_allowed_emails()
        if email_lower not in allowed_emails:
            raise HTTPException(status_code=403, detail="Email not allowed")
        hashed_password = pwd_context.hash(form_data.password)
        db_user = User(email=email_lower, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        user = db_user
    elif not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password. \n If you have forgotten your password please contact the GreenDIGIT team: goncalo.ferreira@student.uva.nl.")
    now = int(time.time())
    token_data = {
        "sub": user.email,
        "iss": JWT_ISSUER,
        "iat": now,
        "nbf": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS,
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get(
    "/token-ui",
    tags=["Auth"],
    summary="Simple HTML login to manually obtain a token",
    description="Convenience page that POSTs to `/login`.",
    response_class=HTMLResponse
)
def token_ui():
    return """
    <html>
    <body>
        <h2>Login to generate token</h2>
        <form action="login" method="post">
            <input name="username" type="email" placeholder="Email" required>
            <input name="password" type="password" placeholder="Password" required>
            <button type="submit">Get Token</button>
        </form>
        <text>The token is only valid for 1 day. You must regenerate in order to access.</text>
        <text>If you have problems loggin in, please contact:</text>
        <ul style="">
            <li>goncalo.ferreira@student.uva.nl</ul>
            <li>a.tahir2@uva.nl</ul>
        </ul>
    </body>
    </html>
    """

@app.post(
    "/submit",
    tags=["Metrics"],
    summary="Submit a metrics JSON payload",
    description=(
        "Stores an arbitrary JSON document as a metric entry.\n\n"
        "**Requires:** `Authorization: Bearer <token>`.\n\n"
        "The `publisher_email` is derived from the token’s `sub` claim."
    ),
    responses={
        200: {"description": "Stored successfully"},
        400: {"description": "Invalid JSON body"},
        401: {"description": "Missing/invalid Bearer token"},
        500: {"description": "Database error"},
    },
)
async def submit(
    request: Request,
    publisher_email: str = Depends(verify_token),
    _example: Any = Body(
        default=None,
        examples={
            "sample": {
                "summary": "Example metric payload",
                "value": {
                    "cpu_watts": 11.2,
                    "mem_bytes": 734003200,
                    "labels": {"node": "compute-0", "job_id": "abc123"}
                },
            }
        },
    ),
):
    body = await request.json()
    ack = store_metric(publisher_email=publisher_email, body=body)
    if not ack.get("ok"):
        raise HTTPException(status_code=500, detail=f"DB error: {ack.get('error')}")
    return {"stored": ack}

@app.get(
    "/metrics/me",
    tags=["Metrics"],
    summary="List my published metrics",
    description=(
        "Returns all metrics published by the authenticated user.\n\n"
        "**Requires:** `Authorization: Bearer <token>`."
    ),
    responses={
        200: {"description": "List of metrics"},
        401: {"description": "Missing/invalid Bearer token"},
    },
)
def get_my_metrics(publisher_email: str = Depends(verify_token)):
    # Query all documents for this publisher
    docs = list(_col.find({"publisher_email": publisher_email}).sort("timestamp", -1))
    # Convert ObjectId and datetime to strings
    for d in docs:
        d["_id"] = str(d["_id"])
        if "timestamp" in d and not isinstance(d["timestamp"], str):
            d["timestamp"] = str(d["timestamp"])
    return docs
