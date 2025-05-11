from enum import Enum
from datetime import datetime
from typing import List, Optional


class TaskStatus(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    DONE = "Done"


class TaskPriority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Task:
    def __init__(self, id: int, title: str, description: str,
                 assignee: Optional[str] = None,
                 priority: TaskPriority = TaskPriority.MEDIUM):
        self.id = id
        self.title = title
        self.description = description
        self.status = TaskStatus.TODO
        self.priority = priority
        self.assignee = assignee
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.comments = []

    def update_status(self, status: TaskStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()

    def add_comment(self, comment: str, author: str) -> None:
        self.comments.append({
            "comment": comment,
            "author": author,
            "timestamp": datetime.now()
        })
        self.updated_at = datetime.now()

    def __str__(self) -> str:
        return f"Task #{self.id}: {self.title} [{self.status.value}] - Assigned to: {self.assignee or 'Unassigned'}"

    def get_details(self) -> str:
        details = [
            f"ID: {self.id}",
            f"Title: {self.title}",
            f"Description: {self.description}",
            f"Status: {self.status.value}",
            f"Priority: {self.priority.value}",
            f"Assignee: {self.assignee or 'Unassigned'}",
            f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')}"
        ]

        if self.comments:
            details.append("\nComments:")
            for idx, comment in enumerate(self.comments, 1):
                details.append(
                    f"  {idx}. [{comment['timestamp'].strftime('%Y-%m-%d %H:%M')}] {comment['author']}: {comment['comment']}")

        return "\n".join(details)