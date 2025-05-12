from typing import List, Dict, Optional
from models.task import Task, TaskStatus, TaskPriority
from patterns.observer import TaskSubject


class TaskService:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
        self.subject = TaskSubject()

    def create_task(self, title: str, description: str,
                    assignee: Optional[str] = None,
                    priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            assignee=assignee,
            priority=priority
        )
        self._tasks[self._next_id] = task
        self._next_id += 1

        # Notify observers
        self.subject.notify(task, "created")
        return task

    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update_task_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        task = self.get_task_by_id(task_id)
        if task:
            old_status = task.status
            task.update_status(status)

            # Notify observers
            self.subject.notify(task, "status_changed")

            return task
        return None

    def assign_task(self, task_id: int, assignee: Optional[str]) -> Optional[Task]:
        task = self.get_task_by_id(task_id)
        if task:
            old_assignee = task.assignee
            task.assignee = assignee

            # Notify observers
            self.subject.notify(task, "assignee_changed")

            return task
        return None

    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            task = self._tasks[task_id]
            del self._tasks[task_id]

            # Notify observers
            self.subject.notify(task, "deleted")

            return True
        return False

    def add_comment(self, task_id: int, comment: str, author: str) -> Optional[Task]:
        task = self.get_task_by_id(task_id)
        if task:
            task.add_comment(comment, author)

            # Notify observers
            self.subject.notify(task, "comment_added")

            return task
        return None

    def filter_tasks(self, filter_strategy) -> List[Task]:
        tasks = self.get_all_tasks()
        return filter_strategy.filter(tasks)