from abc import ABC, abstractmethod
from typing import List, Optional
from models.task import TaskStatus, TaskPriority


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass


class TaskCommand(Command):
    def __init__(self, task_service):
        self.task_service = task_service


class CreateTaskCommand(TaskCommand):
    def __init__(self, task_service, title: str, description: str,
                 assignee: Optional[str] = None,
                 priority: TaskPriority = TaskPriority.MEDIUM):
        super().__init__(task_service)
        self.title = title
        self.description = description
        self.assignee = assignee
        self.priority = priority
        self.created_task_id = None

    def execute(self) -> None:
        task = self.task_service.create_task(
            title=self.title,
            description=self.description,
            assignee=self.assignee,
            priority=self.priority
        )
        self.created_task_id = task.id

    def undo(self) -> None:
        if self.created_task_id is not None:
            self.task_service.delete_task(self.created_task_id)
            self.created_task_id = None


class UpdateTaskStatusCommand(TaskCommand):
    def __init__(self, task_service, task_id: int, new_status: TaskStatus):
        super().__init__(task_service)
        self.task_id = task_id
        self.new_status = new_status
        self.old_status = None

    def execute(self) -> None:
        task = self.task_service.get_task_by_id(self.task_id)
        if task:
            self.old_status = task.status
            self.task_service.update_task_status(self.task_id, self.new_status)

    def undo(self) -> None:
        if self.old_status:
            self.task_service.update_task_status(self.task_id, self.old_status)


class AssignTaskCommand(TaskCommand):
    def __init__(self, task_service, task_id: int, assignee: str):
        super().__init__(task_service)
        self.task_id = task_id
        self.new_assignee = assignee
        self.old_assignee = None

    def execute(self) -> None:
        task = self.task_service.get_task_by_id(self.task_id)
        if task:
            self.old_assignee = task.assignee
            self.task_service.assign_task(self.task_id, self.new_assignee)

    def undo(self) -> None:
        self.task_service.assign_task(self.task_id, self.old_assignee)


class CommandInvoker:
    def __init__(self):
        self._history: List[Command] = []

    def execute_command(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo_last_command(self) -> None:
        if self._history:
            command = self._history.pop()
            command.undo()
            print(f"Undid last command")
        else:
            print("No commands to undo")