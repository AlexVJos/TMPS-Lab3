from abc import ABC, abstractmethod
from typing import List
from models.task import Task, TaskStatus


class Observer(ABC):
    @abstractmethod
    def update(self, task: Task, event_type: str) -> None:
        pass


class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self, task: Task, event_type: str) -> None:
        pass


class TaskSubject(Subject):
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, task: Task, event_type: str) -> None:
        for observer in self._observers:
            observer.update(task, event_type)


class TaskAssigneeObserver(Observer):
    def update(self, task: Task, event_type: str) -> None:
        if task.assignee:
            print(f"\n[NOTIFICATION] {task.assignee}, task '{task.title}' has been {event_type}.")


class TaskManagerObserver(Observer):
    def update(self, task: Task, event_type: str) -> None:
        if event_type == "status_changed" and task.status == TaskStatus.DONE:
            print(f"\n[MANAGER NOTIFICATION] Task '{task.title}' has been marked as completed and requires review.")
        elif event_type == "created":
            print(f"\n[MANAGER NOTIFICATION] New task created: '{task.title}'")


class TaskLogObserver(Observer):
    def update(self, task: Task, event_type: str) -> None:
        print(
            f"\n[LOG] Task #{task.id} '{task.title}' - Event: {event_type} - Time: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")
