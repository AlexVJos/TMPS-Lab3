from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models.task import Task, TaskStatus, TaskPriority


class ReportGenerator(ABC):
    def generate_report(self, tasks: List[Task]) -> str:
        """Template method defining the algorithm structure"""
        filtered_tasks = self.filter_tasks(tasks)
        sorted_tasks = self.sort_tasks(filtered_tasks)
        report_data = self.collect_data(sorted_tasks)
        return self.format_report(report_data)

    @abstractmethod
    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        """Hook for filtering tasks"""
        pass

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Default implementation to sort tasks by ID"""
        return sorted(tasks, key=lambda task: task.id)

    @abstractmethod
    def collect_data(self, tasks: List[Task]) -> Dict[str, Any]:
        """Hook for collecting data for the report"""
        pass

    @abstractmethod
    def format_report(self, data: Dict[str, Any]) -> str:
        """Hook for formatting report output"""
        pass


class StatusReportGenerator(ReportGenerator):
    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        return tasks  # No filtering

    def collect_data(self, tasks: List[Task]) -> Dict[str, Any]:
        status_counts = {status: 0 for status in TaskStatus}
        for task in tasks:
            status_counts[task.status] += 1

        return {
            "total_tasks": len(tasks),
            "status_counts": status_counts
        }

    def format_report(self, data: Dict[str, Any]) -> str:
        report = [
            "=== STATUS REPORT ===",
            f"Total tasks: {data['total_tasks']}",
            "\nTask status breakdown:"
        ]

        for status, count in data["status_counts"].items():
            if count > 0:
                report.append(f"  {status.value}: {count} tasks")

        return "\n".join(report)


class AssigneeReportGenerator(ReportGenerator):
    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        return [task for task in tasks if task.assignee]  # Only assigned tasks

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        return sorted(tasks, key=lambda task: (task.assignee or "", task.id))

    def collect_data(self, tasks: List[Task]) -> Dict[str, Any]:
        assignee_tasks = {}
        for task in tasks:
            if task.assignee not in assignee_tasks:
                assignee_tasks[task.assignee] = []
            assignee_tasks[task.assignee].append(task)

        return {
            "assignee_tasks": assignee_tasks
        }

    def format_report(self, data: Dict[str, Any]) -> str:
        report = ["=== ASSIGNEE WORKLOAD REPORT ==="]

        for assignee, tasks in data["assignee_tasks"].items():
            report.append(f"\n{assignee} - {len(tasks)} tasks:")
            for task in tasks:
                report.append(f"  - Task #{task.id}: {task.title} [{task.status.value}]")

        return "\n".join(report)


class PriorityReportGenerator(ReportGenerator):
    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        return tasks  # No filtering

    def sort_tasks(self, tasks: List[Task]) -> List[Task]:
        # Sort by priority (highest first)
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        return sorted(tasks, key=lambda task: priority_order[task.priority])

    def collect_data(self, tasks: List[Task]) -> Dict[str, Any]:
        priority_tasks = {priority: [] for priority in TaskPriority}
        for task in tasks:
            priority_tasks[task.priority].append(task)

        return {
            "priority_tasks": priority_tasks
        }

    def format_report(self, data: Dict[str, Any]) -> str:
        report = ["=== PRIORITY REPORT ==="]

        priority_order = [
            TaskPriority.CRITICAL,
            TaskPriority.HIGH,
            TaskPriority.MEDIUM,
            TaskPriority.LOW
        ]

        for priority in priority_order:
            tasks = data["priority_tasks"][priority]
            if tasks:
                report.append(f"\n{priority.value} Priority - {len(tasks)} tasks:")
                for task in tasks:
                    status_str = f"[{task.status.value}]"
                    assignee_str = f"- {task.assignee}" if task.assignee else "- Unassigned"
                    report.append(f"  - Task #{task.id}: {task.title} {status_str} {assignee_str}")

        return "\n".join(report)
