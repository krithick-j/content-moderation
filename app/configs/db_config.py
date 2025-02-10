import os
from typing import Annotated, AsyncIterator
from dotenv import load_dotenv
from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.configs.log_config import setup_logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine


setup_logger()
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_ASYNC_URL = os.getenv("DATABASE_ASYNC_URL")
Base = declarative_base()

async_engine = create_async_engine(DATABASE_ASYNC_URL, echo=True, future=True)
async_session = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    future=True,
    expire_on_commit=False
)

async def get_async_db() -> AsyncIterator[async_sessionmaker]:
    try:
        yield async_session()
    except SQLAlchemyError as e:
        logger.exception(e)


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