"""demo script to verify pawpal+ backend logic in the terminal."""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # create an owner
    owner = Owner(name="Jordan")
    print(f"owner: {owner.name}\n")

    # create two pets
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    print(f"pets: {mochi}, {luna}\n")

    # add tasks to mochi (out of order to test sorting)
    mochi.add_task(Task(description="evening walk", time="18:00", priority="high", duration_minutes=30, frequency="daily"))
    mochi.add_task(Task(description="morning walk", time="07:30", priority="high", duration_minutes=30, frequency="daily"))
    mochi.add_task(Task(description="breakfast", time="08:00", priority="high", duration_minutes=10, frequency="daily"))

    # add tasks to luna
    luna.add_task(Task(description="feed luna", time="08:00", priority="high", duration_minutes=10, frequency="daily"))
    luna.add_task(Task(description="play time", time="14:00", priority="medium", duration_minutes=20))
    luna.add_task(Task(description="vet appointment", time="10:00", priority="high", duration_minutes=60, frequency="once"))

    # set up the scheduler
    scheduler = Scheduler(owner)

    # show today's full schedule (sorted by time)
    print("=" * 45)
    print(scheduler.generate_schedule_summary())
    print("=" * 45)

    # test conflict detection (mochi breakfast and luna feeding at 08:00)
    print("\nchecking for conflicts...")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for c in conflicts:
            print(f"  {c}")
    else:
        print("  no conflicts found")

    # test filtering by pet
    print(f"\ntasks for mochi only:")
    for task in scheduler.filter_by_pet("Mochi"):
        print(f"  {task}")

    # test filtering by status
    print(f"\npending tasks: {len(scheduler.filter_by_status(completed=False))}")

    # test marking a task complete and recurring logic
    print("\nmarking 'morning walk' as complete...")
    scheduler.mark_task_complete("Mochi", "morning walk")

    # check that a new occurrence was created
    mochi_tasks = scheduler.filter_by_pet("Mochi")
    print(f"mochi now has {len(mochi_tasks)} tasks (new recurring one added):")
    for task in scheduler.sort_by_time(mochi_tasks):
        print(f"  {task}")

    # show priority sorting
    print("\nall tasks sorted by priority:")
    for task in scheduler.sort_by_priority():
        print(f"  {task}")


if __name__ == "__main__":
    main()
