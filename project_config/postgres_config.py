# project_config/postgres_config.py

from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
DB_USER = "cloud_user"
DB_PASSWORD = "admin123"
DB_NAME = "cloud_metrics_db"
DB_HOST = "localhost"
DB_PORT = 5432

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()