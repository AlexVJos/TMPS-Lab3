from typing import List, Dict
from models.task import Task
from patterns.template_method import ReportGenerator


class ReportService:
    def __init__(self):
        self._generators: Dict[str, ReportGenerator] = {}

    def register_generator(self, name: str, generator: ReportGenerator) -> None:
        self._generators[name] = generator

    def generate_report(self, name: str, tasks: List[Task]) -> str:
        if name in self._generators:
            return self._generators[name].generate_report(tasks)
        else:
            return f"Report generator '{name}' not found"

    def get_available_reports(self) -> List[str]:
        return list(self._generators.keys())