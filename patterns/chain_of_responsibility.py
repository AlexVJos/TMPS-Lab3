from abc import ABC, abstractmethod
from models.task import Task, TaskPriority


class ApprovalHandler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, task: Task) -> str:
        pass


class TeamLeadApprovalHandler(ApprovalHandler):
    def handle(self, task: Task) -> str:
        if task.priority in [TaskPriority.LOW, TaskPriority.MEDIUM]:
            return f"Task '{task.title}' has been approved by Team Lead"
        elif self._next_handler:
            print(f"Task '{task.title}' requires higher level approval. Forwarding to Project Manager...")
            return self._next_handler.handle(task)
        else:
            return f"Task '{task.title}' cannot be approved. No handler available."


class ProjectManagerApprovalHandler(ApprovalHandler):
    def handle(self, task: Task) -> str:
        if task.priority == TaskPriority.HIGH:
            return f"Task '{task.title}' has been approved by Project Manager"
        elif self._next_handler:
            print(f"Task '{task.title}' requires higher level approval. Forwarding to Department Director...")
            return self._next_handler.handle(task)
        else:
            return f"Task '{task.title}' cannot be approved. No handler available."


class DirectorApprovalHandler(ApprovalHandler):
    def handle(self, task: Task) -> str:
        if task.priority == TaskPriority.CRITICAL:
            return f"Task '{task.title}' has been approved by Department Director"
        else:
            return f"Task '{task.title}' cannot be approved. Required approval level not available."
