from abc import ABC, abstractmethod
from typing import List
from models.task import Task, TaskStatus, TaskPriority


class FilterStrategy(ABC):
    @abstractmethod
    def filter(self, tasks: List[Task]) -> List[Task]:
        pass


class StatusFilterStrategy(FilterStrategy):
    def __init__(self, status: TaskStatus):
        self.status = status

    def filter(self, tasks: List[Task]) -> List[Task]:
        return [task for task in tasks if task.status == self.status]


class AssigneeFilterStrategy(FilterStrategy):
    def __init__(self, assignee: str):
        self.assignee = assignee

    def filter(self, tasks: List[Task]) -> List[Task]:
        return [task for task in tasks if task.assignee == self.assignee]


class PriorityFilterStrategy(FilterStrategy):
    def __init__(self, priority: TaskPriority):
        self.priority = priority

    def filter(self, tasks: List[Task]) -> List[Task]:
        return [task for task in tasks if task.priority == self.priority]


class CompositeFilterStrategy(FilterStrategy):
    def __init__(self, strategies: List[FilterStrategy]):
        self.strategies = strategies

    def filter(self, tasks: List[Task]) -> List[Task]:
        result = tasks
        for strategy in self.strategies:
            result = strategy.filter(result)
        return result