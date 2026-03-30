"""tests for the pawpal+ system — covers core behaviors, sorting, recurrence, and conflicts."""

import sys
import os

# make sure we can import from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


# --- task tests ---

def test_task_mark_complete():
    """marking a task complete should change its status."""
    task = Task(description="walk", time="09:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_default_values():
    """tasks should have sensible defaults."""
    task = Task(description="feed", time="08:00")
    assert task.frequency == "once"
    assert task.priority == "medium"
    assert task.duration_minutes == 15
    assert task.completed is False


# --- pet tests ---

def test_pet_add_task():
    """adding a task to a pet should increase the task count."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(description="walk", time="09:00"))
    assert len(pet.tasks) == 1


def test_pet_add_task_sets_pet_name():
    """adding a task should tag it with the pet's name."""
    pet = Pet(name="Luna", species="cat")
    task = Task(description="feed", time="08:00")
    pet.add_task(task)
    assert task.pet_name == "Luna"


def test_pet_remove_task():
    """removing a task by description should work."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="walk", time="09:00"))
    pet.add_task(Task(description="feed", time="10:00"))
    pet.remove_task("walk")
    assert len(pet.tasks) == 1
    assert pet.tasks[0].description == "feed"


def test_pet_get_pending_tasks():
    """should only return tasks that aren't done yet."""
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(description="walk", time="09:00")
    t2 = Task(description="feed", time="10:00")
    t2.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].description == "walk"


# --- owner tests ---

def test_owner_add_pet():
    """adding a pet should increase the owner's pet count."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))
    assert len(owner.pets) == 1


def test_owner_get_all_tasks():
    """should collect tasks from all pets."""
    owner = Owner(name="Jordan")
    p1 = Pet(name="Mochi", species="dog")
    p2 = Pet(name="Luna", species="cat")
    p1.add_task(Task(description="walk", time="09:00"))
    p2.add_task(Task(description="feed", time="08:00"))
    owner.add_pet(p1)
    owner.add_pet(p2)
    assert len(owner.get_all_tasks()) == 2


def test_owner_find_pet():
    """should find a pet by name or return none."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))
    assert owner.find_pet("Mochi") is not None
    assert owner.find_pet("Ghost") is None


# --- scheduler tests ---

def _make_scheduler():
    """helper to set up a scheduler with sample data."""
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")

    mochi.add_task(Task(description="evening walk", time="18:00", priority="low"))
    mochi.add_task(Task(description="morning walk", time="07:30", priority="high"))
    luna.add_task(Task(description="feed luna", time="08:00", priority="medium"))

    owner.add_pet(mochi)
    owner.add_pet(luna)
    return Scheduler(owner)


def test_sort_by_time():
    """tasks should come back in chronological order."""
    scheduler = _make_scheduler()
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == ["07:30", "08:00", "18:00"]


def test_sort_by_priority():
    """tasks should be sorted high > medium > low."""
    scheduler = _make_scheduler()
    sorted_tasks = scheduler.sort_by_priority()
    priorities = [t.priority for t in sorted_tasks]
    assert priorities == ["high", "medium", "low"]


def test_filter_by_status():
    """should separate completed from pending tasks."""
    scheduler = _make_scheduler()
    # mark one task complete
    scheduler.mark_task_complete("Mochi", "morning walk")
    completed = scheduler.filter_by_status(completed=True)
    pending = scheduler.filter_by_status(completed=False)
    assert len(completed) == 1
    assert completed[0].description == "morning walk"
    assert len(pending) >= 2


def test_filter_by_pet():
    """should only return tasks for the given pet."""
    scheduler = _make_scheduler()
    mochi_tasks = scheduler.filter_by_pet("Mochi")
    assert all(t.pet_name == "Mochi" for t in mochi_tasks)
    assert len(mochi_tasks) == 2


def test_detect_conflicts():
    """tasks at the same time should trigger a conflict warning."""
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")

    mochi.add_task(Task(description="walk mochi", time="08:00"))
    luna.add_task(Task(description="feed luna", time="08:00"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_no_conflicts_when_different_times():
    """no conflicts when tasks are at different times."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="walk", time="08:00"))
    pet.add_task(Task(description="feed", time="09:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0


def test_recurring_daily_task():
    """completing a daily task should create a new one."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="morning walk", time="07:30", frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    assert len(pet.tasks) == 1

    scheduler.mark_task_complete("Mochi", "morning walk")

    # original is done, plus a new one was added
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False
    assert pet.tasks[1].frequency == "daily"


def test_non_recurring_task_no_duplicate():
    """completing a one-time task should not create a new one."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="vet visit", time="10:00", frequency="once"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Mochi", "vet visit")

    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


def test_pet_with_no_tasks():
    """a pet with no tasks should not break the scheduler."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Ghost", species="hamster"))
    scheduler = Scheduler(owner)
    assert scheduler.get_todays_schedule() == []
    assert scheduler.detect_conflicts() == []


def test_schedule_summary_output():
    """the summary should contain the owner's name."""
    scheduler = _make_scheduler()
    summary = scheduler.generate_schedule_summary()
    assert "Jordan" in summary
