from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
import time
import os

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, Session

app = FastAPI()
security = HTTPBearer()

# Secret key for JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600

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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# @app.post("/register")
# def register(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
#     allowed_emails = load_allowed_emails()
#     email_lower = email.strip().lower()
#     if email_lower not in allowed_emails:
#         raise HTTPException(status_code=403, detail="Email not allowed")
#     user = db.query(User).filter(User.email == email_lower).first()
#     if user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     hashed_password = pwd_context.hash(password)
#     db_user = User(email=email_lower, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return {"msg": "User registered"}

@app.post("/login")
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
        raise HTTPException(status_code=400, detail="Incorrect password")
    token_data = {
        "sub": user.email,
        "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/token-ui", response_class=HTMLResponse)
def token_ui():
    return """
    <html>
    <body>
        <h2>Login to generate token</h2>
        <form action="/login" method="post">
            <input name="username" type="email" placeholder="Email" required>
            <input name="password" type="password" placeholder="Password" required>
            <button type="submit">Get Token</button>
        </form>
    </body>
    </html>
    """

@app.get("/submit")
async def submit(
    request: Request,
    token: None = Depends(verify_token)
):
    data = await request.json()
    # Optionally, validate data with SubmitData(**data)
    return {"received": data}