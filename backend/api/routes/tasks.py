from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, get_queue
from db.models import Task
from db.schemas import TaskCreate, TaskResponse
from worker.redis_queue import TaskQueue

router = APIRouter()


@router.get("", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id.desc()).all()


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        name=body.name,
        env_type=body.env_type,
        env_name=body.env_name,
        algo=body.algo,
        config=body.config,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()