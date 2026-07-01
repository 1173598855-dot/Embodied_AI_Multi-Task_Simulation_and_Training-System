class TrainingLogService:
    def __init__(self, training_log_repository):
        self.training_log_repository = training_log_repository

    def list_logs(self, task_id: int):
        return self.training_log_repository.list_by_task(task_id)
