# reset_password_admin.py
import sys
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from login_server import User, Base  # Reuse your model definition

if len(sys.argv) != 3:
    print("Usage: python reset_password_admin.py <email> <new_password>")
    sys.exit(1)

email = sys.argv[1].strip().lower()
new_password = sys.argv[2]

# Same bcrypt context as in login_server.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to the same SQLite DB
engine = create_engine("sqlite:///./users.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

user = db.query(User).filter(User.email == email).first()
if not user:
    print(f"User with email {email} not found.")
    sys.exit(1)

# Update hashed password
user.hashed_password = pwd_context.hash(new_password)
db.commit()

print(f"Password for {email} updated successfully.")
