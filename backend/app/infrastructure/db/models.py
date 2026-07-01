from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.db.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    env_type = Column(String(32), nullable=False, default="gym")
    env_name = Column(String(64), nullable=False, default="CartPole-v1")
    algo = Column(String(32), nullable=False, default="q_learning")
    status = Column(String(20), nullable=False, default="created")
    config = Column(JSON, nullable=True)
    total_reward = Column(Float, nullable=True)
    current_run_id = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    logs = relationship("TrainingLogModel", back_populates="task", cascade="all, delete-orphan")


class TrainingLogModel(Base):
    __tablename__ = "training_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(String(64), nullable=True)
    episode = Column(Integer, nullable=False)
    step = Column(Integer, nullable=False)
    reward = Column(Float, nullable=False)
    avg_reward = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    task = relationship("TaskModel", back_populates="logs")
