from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, get_queue
from db.models import Task, TrainingLog
from db.schemas import TrainingLogResponse
from worker.redis_queue import TaskQueue
from core.task_state import can_start_task

router = APIRouter()


@router.post("/{task_id}/start")
def start_training(task_id: int, db: Session = Depends(get_db), queue: TaskQueue = Depends(get_queue)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not can_start_task(task.status):
        raise HTTPException(status_code=400, detail=f"Task cannot be started from status {task.status}")

    task.status = "pending"
    db.commit()
    queue.clear_control_command(task_id)
    queue.push(task_id)
    queue.update_status(task_id, {"status": "pending"})
    return {"message": "Task queued", "task_id": task_id}


@router.post("/{task_id}/pause")
def pause_training(task_id: int, db: Session = Depends(get_db), queue: TaskQueue = Depends(get_queue)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status not in {"running", "pending"}:
        raise HTTPException(status_code=400, detail=f"Task cannot be paused from status {task.status}")
    task.status = "paused"
    db.commit()
    queue.set_control_command(task_id, "pause")
    queue.update_status(task_id, {"status": "paused"})
    return {"message": "Task paused", "task_id": task_id}


@router.post("/{task_id}/cancel")
def cancel_training(task_id: int, db: Session = Depends(get_db), queue: TaskQueue = Depends(get_queue)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status in {"completed", "failed", "canceled"}:
        raise HTTPException(status_code=400, detail=f"Task cannot be canceled from status {task.status}")
    task.status = "canceled"
    db.commit()
    queue.set_control_command(task_id, "cancel")
    queue.update_status(task_id, {"status": "canceled"})
    return {"message": "Task canceled", "task_id": task_id}


@router.get("/{task_id}/logs", response_model=list[TrainingLogResponse])
def get_training_logs(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return (
        db.query(TrainingLog)
        .filter(TrainingLog.task_id == task_id)
        .order_by(TrainingLog.episode.asc())
        .all()
    )
