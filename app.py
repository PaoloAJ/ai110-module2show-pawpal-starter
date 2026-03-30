"""pawpal+ streamlit app — connects the ui to the backend scheduling logic."""

import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("a smart pet care management system")

# --- session state setup ---
# use session state so our data persists between reruns
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# --- owner setup ---
st.subheader("Owner Info")
owner_name = st.text_input("Owner name", value="Jordan")

if st.session_state.owner is None or st.session_state.owner.name != owner_name:
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.divider()

# --- add a pet ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "hamster", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    if owner.find_pet(pet_name):
        st.warning(f"{pet_name} already exists!")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age=age))
        st.success(f"added {pet_name} the {species}!")

# show current pets
if owner.pets:
    st.markdown("**Your pets:**")
    for pet in owner.pets:
        st.write(f"- {pet}")
else:
    st.info("no pets yet. add one above!")

st.divider()

# --- add a task ---
st.subheader("Schedule a Task")

if not owner.pets:
    st.info("add a pet first before scheduling tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet = st.selectbox("Assign to pet", pet_names)

    col1, col2 = st.columns(2)
    with col1:
        task_desc = st.text_input("Task description", value="Morning walk")
        task_time = st.time_input("Scheduled time")
    with col2:
        task_priority = st.selectbox("Priority", ["high", "medium", "low"])
        task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

    task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        time_str = task_time.strftime("%H:%M")
        new_task = Task(
            description=task_desc,
            time=time_str,
            priority=task_priority,
            duration_minutes=int(task_duration),
            frequency=task_frequency,
        )
        pet = owner.find_pet(selected_pet)
        if pet:
            pet.add_task(new_task)
            st.success(f"added '{task_desc}' for {selected_pet} at {time_str}!")

st.divider()

# --- today's schedule ---
st.subheader("Today's Schedule")

if owner.pets and scheduler.get_all_tasks():
    # show conflict warnings
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for c in conflicts:
            st.warning(c)

    # show sorted schedule
    schedule = scheduler.get_todays_schedule()
    if schedule:
        # build a table of tasks
        table_data = []
        for task in schedule:
            table_data.append({
                "time": task.time,
                "task": task.description,
                "pet": task.pet_name,
                "priority": task.priority,
                "duration": f"{task.duration_minutes} min",
                "frequency": task.frequency,
                "status": "done" if task.completed else "pending",
            })
        st.table(table_data)
    else:
        st.success("all tasks completed!")

    # mark tasks complete
    st.markdown("**Mark a task as complete:**")
    pending = scheduler.filter_by_status(completed=False)
    if pending:
        task_options = [f"{t.pet_name}: {t.description} ({t.time})" for t in pending]
        selected_task = st.selectbox("Select task to complete", task_options)
        if st.button("Mark complete"):
            # parse the selection to get pet name and description
            parts = selected_task.split(": ", 1)
            p_name = parts[0]
            desc = parts[1].rsplit(" (", 1)[0]
            result = scheduler.mark_task_complete(p_name, desc)
            if result:
                st.success(f"marked '{desc}' as complete!")
                if result.frequency in ("daily", "weekly"):
                    st.info(f"a new {result.frequency} occurrence has been scheduled.")
                st.rerun()
    else:
        st.success("no pending tasks!")

    st.divider()

    # --- filter view ---
    st.subheader("Filter Tasks")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_pet = st.selectbox("Filter by pet", ["all"] + [p.name for p in owner.pets])
    with filter_col2:
        filter_status = st.selectbox("Filter by status", ["all", "pending", "completed"])

    filtered = scheduler.get_all_tasks()
    if filter_pet != "all":
        filtered = scheduler.filter_by_pet(filter_pet, filtered)
    if filter_status == "pending":
        filtered = scheduler.filter_by_status(False, filtered)
    elif filter_status == "completed":
        filtered = scheduler.filter_by_status(True, filtered)

    filtered = scheduler.sort_by_time(filtered)

    if filtered:
        filter_data = []
        for task in filtered:
            filter_data.append({
                "time": task.time,
                "task": task.description,
                "pet": task.pet_name,
                "priority": task.priority,
                "status": "done" if task.completed else "pending",
            })
        st.table(filter_data)
    else:
        st.info("no tasks match your filters.")
else:
    st.info("add pets and tasks to see your schedule!")
