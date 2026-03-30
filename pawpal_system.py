"""pawpal+ backend logic layer — classes for managing pet care tasks and scheduling."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Task:
    """represents a single pet care task like a walk, feeding, or vet visit."""

    description: str
    time: str  # format "HH:MM"
    frequency: str = "once"  # "once", "daily", or "weekly"
    priority: str = "medium"  # "low", "medium", "high"
    duration_minutes: int = 15
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self):
        """marks this task as done."""
        self.completed = True

    def __str__(self):
        status = "done" if self.completed else "pending"
        return f"[{status}] {self.time} - {self.description} ({self.priority}, {self.duration_minutes}min)"


@dataclass
class Pet:
    """stores pet details and holds a list of tasks."""

    name: str
    species: str
    age: int = 0
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """adds a task to this pet's task list."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, description: str):
        """removes a task by its description."""
        self.tasks = [t for t in self.tasks if t.description != description]

    def get_pending_tasks(self):
        """returns tasks that haven't been completed yet."""
        return [t for t in self.tasks if not t.completed]

    def __str__(self):
        return f"{self.name} ({self.species}, age {self.age}) — {len(self.tasks)} tasks"


@dataclass
class Owner:
    """manages multiple pets and gives access to all their tasks."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """adds a pet to the owner's list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """removes a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self):
        """collects all tasks from all pets into one list."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def find_pet(self, pet_name: str) -> Optional[Pet]:
        """finds a pet by name, returns none if not found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def __str__(self):
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "no pets"
        return f"{self.name} — pets: {pet_names}"


class Scheduler:
    """the brain of pawpal+ — retrieves, sorts, filters, and manages tasks across pets."""

    def __init__(self, owner: Owner):
        """sets up the scheduler with a reference to the owner."""
        self.owner = owner

    def get_all_tasks(self):
        """gets every task from every pet the owner has."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: Optional[list] = None):
        """sorts tasks by their scheduled time (earliest first)."""
        if tasks is None:
            tasks = self.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks: Optional[list] = None):
        """sorts tasks by priority (high first, then medium, then low)."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        if tasks is None:
            tasks = self.get_all_tasks()
        return sorted(tasks, key=lambda t: priority_order.get(t.priority, 1))

    def filter_by_status(self, completed: bool, tasks: Optional[list] = None):
        """filters tasks by whether they are completed or not."""
        if tasks is None:
            tasks = self.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str, tasks: Optional[list] = None):
        """filters tasks to only show ones for a specific pet."""
        if tasks is None:
            tasks = self.get_all_tasks()
        return [t for t in tasks if t.pet_name == pet_name]

    def detect_conflicts(self, tasks: Optional[list] = None):
        """checks if any two tasks are scheduled at the same time and returns warnings."""
        if tasks is None:
            tasks = self.get_all_tasks()
        conflicts = []
        seen = {}
        for task in tasks:
            if task.time in seen:
                conflicts.append(
                    f"conflict: '{task.description}' ({task.pet_name}) and "
                    f"'{seen[task.time].description}' ({seen[task.time].pet_name}) "
                    f"are both at {task.time}"
                )
            else:
                seen[task.time] = task
        return conflicts

    def mark_task_complete(self, pet_name: str, description: str):
        """marks a task as complete and handles recurring tasks."""
        pet = self.owner.find_pet(pet_name)
        if pet is None:
            return None

        for task in pet.tasks:
            if task.description == description and not task.completed:
                task.mark_complete()
                # if it's a recurring task, create the next occurrence
                new_task = self._create_next_occurrence(task)
                if new_task:
                    pet.add_task(new_task)
                return task
        return None

    def _create_next_occurrence(self, task: Task):
        """creates the next occurrence of a recurring task."""
        if task.frequency == "once":
            return None

        today = datetime.now()
        if task.frequency == "daily":
            next_date = today + timedelta(days=1)
        elif task.frequency == "weekly":
            next_date = today + timedelta(weeks=1)
        else:
            return None

        # new task with the same details but not completed
        return Task(
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            priority=task.priority,
            duration_minutes=task.duration_minutes,
            completed=False,
            pet_name=task.pet_name,
        )

    def get_todays_schedule(self):
        """builds a sorted schedule of all pending tasks for today."""
        pending = self.filter_by_status(completed=False)
        return self.sort_by_time(pending)

    def generate_schedule_summary(self):
        """creates a readable text summary of today's schedule."""
        schedule = self.get_todays_schedule()
        conflicts = self.detect_conflicts(schedule)

        lines = []
        lines.append(f"schedule for {self.owner.name}:")
        lines.append("-" * 40)

        if not schedule:
            lines.append("no tasks scheduled!")
        else:
            for task in schedule:
                lines.append(f"  {task}")

        if conflicts:
            lines.append("")
            lines.append("warnings:")
            for c in conflicts:
                lines.append(f"  {c}")

        return "\n".join(lines)
