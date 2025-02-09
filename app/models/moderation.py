from sqlalchemy import Column, String, Integer, JSON
from app.configs.db_config import Base


class ModerationResult(Base):
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=True, index=True)
    task_id = Column(String)
    status = Column(String)
    results = Column(JSON)