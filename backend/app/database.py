from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Default to MySQL for production/docker, fallback to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://hitl_user:hitl_password@db:3306/hitl_db")

# For MySQL, we use pymysql driver
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = "mysql+pymysql" + DATABASE_URL[5:]

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
