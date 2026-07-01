from sqlalchemy.orm import Session

from app.infrastructure.db.models import TaskModel, TrainingLogModel


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, env_type: str, env_name: str, algo: str, config: dict | None) -> TaskModel:
        task = TaskModel(
            name=name,
            env_type=env_type,
            env_name=env_name,
            algo=algo,
            config=config,
            status="created",
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: int) -> TaskModel | None:
        return self.session.query(TaskModel).filter(TaskModel.id == task_id).first()

    def list(self) -> list[TaskModel]:
        return self.session.query(TaskModel).order_by(TaskModel.id.desc()).all()

    def delete(self, task_id: int) -> None:
        task = self.get(task_id)
        if task is not None:
            self.session.delete(task)
            self.session.commit()

    def set_status(self, task_id: int, status: str) -> TaskModel | None:
        task = self.get(task_id)
        if task is None:
            return None
        task.status = status
        self.session.commit()
        self.session.refresh(task)
        return task

    def set_run(self, task_id: int, run_id: str | None) -> TaskModel | None:
        task = self.get(task_id)
        if task is None:
            return None
        task.current_run_id = run_id
        self.session.commit()
        self.session.refresh(task)
        return task

    def set_total_reward(self, task_id: int, total_reward: float | None) -> TaskModel | None:
        task = self.get(task_id)
        if task is None:
            return None
        task.total_reward = total_reward
        self.session.commit()
        self.session.refresh(task)
        return task

    def set_error(self, task_id: int, error_message: str | None) -> TaskModel | None:
        task = self.get(task_id)
        if task is None:
            return None
        task.error_message = error_message
        self.session.commit()
        self.session.refresh(task)
        return task


class TrainingLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        task_id: int,
        run_id: str | None,
        episode: int,
        step: int,
        reward: float,
        avg_reward: float | None,
    ) -> TrainingLogModel:
        log = TrainingLogModel(
            task_id=task_id,
            run_id=run_id,
            episode=episode,
            step=step,
            reward=reward,
            avg_reward=avg_reward,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_by_task(self, task_id: int) -> list[TrainingLogModel]:
        return (
            self.session.query(TrainingLogModel)
            .filter(TrainingLogModel.task_id == task_id)
            .order_by(TrainingLogModel.episode.asc())
            .all()
        )

    def delete_by_task(self, task_id: int) -> None:
        self.session.query(TrainingLogModel).filter(TrainingLogModel.task_id == task_id).delete()
        self.session.commit()
