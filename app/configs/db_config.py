import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from loguru import logger
from app.configs.log_config import setup_logger

setup_logger()
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

logger.info("Creating database engine")
engine = create_engine(DATABASE_URL)

logger.info("Creating session local")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger.info("Creating declarative base")
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()