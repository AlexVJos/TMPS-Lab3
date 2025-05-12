import os
from models.task import Task, TaskStatus, TaskPriority
from models.user import User
from patterns.observer import TaskAssigneeObserver, TaskManagerObserver, TaskLogObserver
from patterns.command import CommandInvoker, CreateTaskCommand, UpdateTaskStatusCommand, AssignTaskCommand
from patterns.strategy import StatusFilterStrategy, AssigneeFilterStrategy, PriorityFilterStrategy, \
    CompositeFilterStrategy
from patterns.template_method import StatusReportGenerator, AssigneeReportGenerator, PriorityReportGenerator
from patterns.chain_of_responsibility import TeamLeadApprovalHandler, ProjectManagerApprovalHandler, \
    DirectorApprovalHandler
from services.task_service import TaskService
from services.report_service import ReportService


class ProjectManagementCLI:
    def __init__(self):
        self.task_service = TaskService()
        self.report_service = ReportService()

        self.report_service.register_generator("status", StatusReportGenerator())
        self.report_service.register_generator("assignee", AssigneeReportGenerator())
        self.report_service.register_generator("priority", PriorityReportGenerator())

        self.command_invoker = CommandInvoker()

        self.team_lead = TeamLeadApprovalHandler()
        self.project_manager = ProjectManagerApprovalHandler()
        self.director = DirectorApprovalHandler()

        self.team_lead.set_next(self.project_manager).set_next(self.director)

        self.assignee_observer = TaskAssigneeObserver()
        self.manager_observer = TaskManagerObserver()
        self.log_observer = TaskLogObserver()

        self.task_service.subject.attach(self.assignee_observer)
        self.task_service.subject.attach(self.manager_observer)
        self.task_service.subject.attach(self.log_observer)

        self.current_user = User("admin", "Administrator")

        self._create_sample_data()

    def _create_sample_data(self):
        self.command_invoker.execute_command(
            CreateTaskCommand(
                self.task_service,
                "Implement login feature",
                "Create login UI and authentication logic",
                "alex",
                TaskPriority.HIGH
            )
        )

        self.command_invoker.execute_command(
            CreateTaskCommand(
                self.task_service,
                "Design database schema",
                "Create ER diagram and SQL scripts",
                "maria",
                TaskPriority.MEDIUM
            )
        )

        self.command_invoker.execute_command(
            CreateTaskCommand(
                self.task_service,
                "Fix security vulnerability",
                "Address CVE-2023-xxxxx in authentication module",
                "alex",
                TaskPriority.CRITICAL
            )
        )

        self.command_invoker.execute_command(
            CreateTaskCommand(
                self.task_service,
                "Update documentation",
                "Update user guide with new features",
                "sam",
                TaskPriority.LOW
            )
        )

        # Update some statuses
        self.command_invoker.execute_command(
            UpdateTaskStatusCommand(
                self.task_service,
                2,
                TaskStatus.IN_PROGRESS
            )
        )

        self.command_invoker.execute_command(
            UpdateTaskStatusCommand(
                self.task_service,
                4,
                TaskStatus.DONE
            )
        )

    def display_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        menu = [
            "\n=== Project Management System ===",
            f"Current user: {self.current_user}",
            "\nOptions:",
            "1. List all tasks",
            "2. View task details",
            "3. Create new task",
            "4. Update task status",
            "5. Assign task",
            "6. Add comment to task",
            "7. Filter tasks",
            "8. Generate report",
            "9. Request task approval",
            "10. Undo last action",
            "0. Exit"
        ]
        print("\n".join(menu))

    def run(self):
        while True:
            try:
                self.display_menu()
                choice = input("\nEnter your choice (0-10): ")
                choice = int(choice)

                if choice == 0:
                    print("\nExiting Project Management System. Goodbye!")
                    break
                elif choice == 1:
                    self.list_all_tasks()
                elif choice == 2:
                    self.view_task_details()
                elif choice == 3:
                    self.create_new_task()
                elif choice == 4:
                    self.update_task_status()
                elif choice == 5:
                    self.assign_task()
                elif choice == 6:
                    self.add_comment()
                elif choice == 7:
                    self.filter_tasks()
                elif choice == 8:
                    self.generate_report()
                elif choice == 9:
                    self.request_approval()
                elif choice == 10:
                    self.command_invoker.undo_last_command()
                else:
                    print("\nInvalid choice. Please select a number between 0 and 10.")

                input("\nPress Enter to continue...")
            except ValueError:
                print("\nInvalid input. Please enter a valid number.")
                input("\nPress Enter to continue...")
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                input("\nPress Enter to continue...")

    def list_all_tasks(self):
        tasks = self.task_service.get_all_tasks()
        if not tasks:
            print("\nNo tasks found.")
            return

        print("\n=== All Tasks ===")
        for task in tasks:
            print(task)

    def view_task_details(self):
        try:
            task_id = int(input("\nEnter task ID: "))
            task = self.task_service.get_task_by_id(task_id)

            if task:
                print("\n" + task.get_details())
            else:
                print(f"\nTask with ID {task_id} not found.")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    def create_new_task(self):
        try:
            title = input("\nTask title: ")
            description = input("Task description: ")
            assignee = input("Assignee (leave empty for unassigned): ") or None

            print("\nPriority levels:")
            for idx, priority in enumerate(TaskPriority, 1):
                print(f"{idx}. {priority.value}")

            priority_choice = int(input("Select priority (1-4): "))
            if not 1 <= priority_choice <= 4:
                print("\nInvalid priority choice. Please select a number between 1 and 4.")
                return

            priority = list(TaskPriority)[priority_choice - 1]

            command = CreateTaskCommand(
                self.task_service,
                title,
                description,
                assignee,
                priority
            )

            self.command_invoker.execute_command(command)
            print("\nTask created successfully!")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    def update_task_status(self):
        try:
            task_id = int(input("\nEnter task ID: "))
            task = self.task_service.get_task_by_id(task_id)

            if not task:
                print(f"\nTask with ID {task_id} not found.")
                return

            print("\nStatus options:")
            for idx, status in enumerate(TaskStatus, 1):
                print(f"{idx}. {status.value}")

            status_choice = int(input("Select new status (1-4): "))
            if not 1 <= status_choice <= 4:
                print("\nInvalid status choice. Please select a number between 1 and 4.")
                return

            new_status = list(TaskStatus)[status_choice - 1]

            command = UpdateTaskStatusCommand(
                self.task_service,
                task_id,
                new_status
            )

            self.command_invoker.execute_command(command)
            print("\nTask status updated successfully!")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    def assign_task(self):
        try:
            task_id = int(input("\nEnter task ID: "))
            task = self.task_service.get_task_by_id(task_id)

            if not task:
                print(f"\nTask with ID {task_id} not found.")
                return

            assignee = input(f"Enter assignee name (current: {task.assignee or 'Unassigned'}): ")
            assignee = assignee if assignee.strip() else None  # Treat empty input as None

            command = AssignTaskCommand(
                self.task_service,
                task_id,
                assignee
            )

            self.command_invoker.execute_command(command)
            print("\nTask assigned successfully!")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    def add_comment(self):
        try:
            task_id = int(input("\nEnter task ID: "))
            task = self.task_service.get_task_by_id(task_id)

            if not task:
                print(f"\nTask with ID {task_id} not found.")
                return

            comment = input("Enter your comment: ")

            self.task_service.add_comment(task_id, comment, self.current_user.username)
            print("\nComment added successfully!")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    def generate_report(self):
        try:
            print("\nAvailable reports:")
            available_reports = self.report_service.get_available_reports()
            for idx, report_name in enumerate(available_reports, 1):
                print(f"{idx}. {report_name.capitalize()} Report")

            choice = int(input("Select report type: "))
            if 1 <= choice <= len(available_reports):
                report_name = available_reports[choice - 1]
                tasks = self.task_service.get_all_tasks()
                report = self.report_service.generate_report(report_name, tasks)
                print(f"\n{report}")
            else:
                print("\nInvalid choice.")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    def request_approval(self):
        try:
            task_id = int(input("\nEnter task ID for approval: "))
            task = self.task_service.get_task_by_id(task_id)

            if not task:
                print(f"\nTask with ID {task_id} not found.")
                return

            print(f"\nRequesting approval for task: {task.title} (Priority: {task.priority.value})")
            result = self.team_lead.handle(task)
            print(f"\nResult: {result}")
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    def filter_tasks(self):
        try:
            print("\nFilter options:")
            print("1. Filter by status")
            print("2. Filter by assignee")
            print("3. Filter by priority")
            print("4. Combined filter")

            choice = int(input("Select filter type: "))

            if choice == 1:
                print("\nStatus options:")
                for idx, status in enumerate(TaskStatus, 1):
                    print(f"{idx}. {status.value}")

                status_choice = int(input("Select status (1-4): "))
                if not 1 <= status_choice <= 4:
                    print("\nInvalid status choice. Please select a number between 1 and 4.")
                    return

                status = list(TaskStatus)[status_choice - 1]

                strategy = StatusFilterStrategy(status)
                filtered_tasks = self.task_service.filter_tasks(strategy)

                print(f"\n=== Tasks with status: {status.value} ===")

            elif choice == 2:
                assignee = input("\nEnter assignee name: ")
                strategy = AssigneeFilterStrategy(assignee)
                filtered_tasks = self.task_service.filter_tasks(strategy)

                print(f"\n=== Tasks assigned to: {assignee} ===")

            elif choice == 3:
                print("\nPriority options:")
                for idx, priority in enumerate(TaskPriority, 1):
                    print(f"{idx}. {priority.value}")

                priority_choice = int(input("Select priority (1-4): "))
                if not 1 <= priority_choice <= 4:
                    print("\nInvalid priority choice. Please select a number between 1 and 4.")
                    return

                priority = list(TaskPriority)[priority_choice - 1]

                strategy = PriorityFilterStrategy(priority)
                filtered_tasks = self.task_service.filter_tasks(strategy)

                print(f"\n=== Tasks with priority: {priority.value} ===")

            elif choice == 4:
                strategies = []

                if input("\nFilter by status? (y/n): ").lower() == 'y':
                    print("Status options:")
                    for idx, status in enumerate(TaskStatus, 1):
                        print(f"{idx}. {status.value}")

                    status_choice = int(input("Select status (1-4): "))
                    if not 1 <= status_choice <= 4:
                        print("\nInvalid status choice. Please select a number between 1 and 4.")
                        return
                    status = list(TaskStatus)[status_choice - 1]
                    strategies.append(StatusFilterStrategy(status))

                if input("Filter by assignee? (y/n): ").lower() == 'y':
                    assignee = input("Enter assignee name: ")
                    strategies.append(AssigneeFilterStrategy(assignee))

                if input("Filter by priority? (y/n): ").lower() == 'y':
                    print("Priority options:")
                    for idx, priority in enumerate(TaskPriority, 1):
                        print(f"{idx}. {priority.value}")

                    priority_choice = int(input("Select priority (1-4): "))
                    if not 1 <= priority_choice <= 4:
                        print("\nInvalid priority choice. Please select a number between 1 and 4.")
                        return
                    priority = list(TaskPriority)[priority_choice - 1]
                    strategies.append(PriorityFilterStrategy(priority))

                strategy = CompositeFilterStrategy(strategies)
                filtered_tasks = self.task_service.filter_tasks(strategy)

                print("\n=== Tasks matching combined filters ===")

            else:
                print("\nInvalid choice.")
                return

            if not filtered_tasks:
                print("No tasks match the filter criteria.")
                return

            for task in filtered_tasks:
                print(task)
        except ValueError:
            print("\nInvalid input. Please enter a valid number.")


if __name__ == "__main__":
    app = ProjectManagementCLI()
    app.run()