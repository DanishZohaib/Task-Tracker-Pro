import streamlit as st
from datetime import datetime
import database
from components.custom_styles import inject_custom_css
from config import AGING_HIGH_THRESHOLD_DAYS, AGING_MEDIUM_THRESHOLD_DAYS

inject_custom_css()

if "current_user" not in st.session_state or st.session_state.current_user is None:
    st.warning("Please log in first to access the Task Manager.")
    st.switch_page("app.py")
    st.stop()

st.title("📝 Task Manager")
st.write(f"Logged in as: **{st.session_state.current_user}**")

# Priority calculations helper
def get_priority_details(created_dt, status):
    if not created_dt:
        return "Normal", "🟢", 0
    age_days = (datetime.now() - created_dt).days
    if age_days < 0:
        age_days = 0
    if status == "Completed":
        return "Normal", "🟢", age_days
    
    if age_days >= AGING_HIGH_THRESHOLD_DAYS:
        return "High", "🔴", age_days
    elif age_days >= AGING_MEDIUM_THRESHOLD_DAYS:
        return "Medium", "🟡", age_days
    else:
        return "Normal", "🟢", age_days

def save_task_changes(task_id):
    title_key = f"edit_title_{task_id}"
    desc_key = f"edit_desc_{task_id}"
    if title_key in st.session_state and desc_key in st.session_state:
        title_val = st.session_state[title_key].strip()
        desc_val = st.session_state[desc_key].strip()
        if title_val:
            database.edit_task(
                task_id=task_id,
                title=title_val,
                description=desc_val,
                edited_by=st.session_state.current_user
            )
            st.session_state[f"toggle_edit_{task_id}"] = False
            st.session_state[f"show_success_edit_{task_id}"] = True

# Create tabs for Workspace operations
tab_workspace, tab_create = st.tabs(["📋 Tasks Board", "➕ Create New Task"])

# Tab 1: Tasks Board
with tab_workspace:
    # Fetch latest tasks
    tasks = database.get_tasks()
    
    if not tasks:
        st.info("No tasks registered in the workspace yet. Use the 'Create New Task' tab to add tasks!")
    else:
        pending_tasks = [t for t in tasks if t.status == "Pending"]
        completed_tasks = [t for t in tasks if t.status == "Completed"]
        
        # Sort pending tasks by oldest first (Created DateTime ascending)
        pending_tasks = sorted(pending_tasks, key=lambda x: x.created_datetime or datetime.min)
        # Sort completed tasks by completion date (newest first)
        completed_tasks = sorted(completed_tasks, key=lambda x: x.completed_datetime or datetime.min, reverse=True)
        
        col_left, col_right = st.columns(2)
        
        # LEFT COLUMN: Pending Tasks (Editable, Completable)
        with col_left:
            st.markdown("### ⏳ Pending Tasks")
            if not pending_tasks:
                st.success("🎉 No pending tasks! All caught up.")
            else:
                for idx, task in enumerate(pending_tasks):
                    p_name, p_icon, age_days = get_priority_details(task.created_datetime, task.status)
                    
                    # Compute title text
                    edited_label = " :green-background[Edited]" if task.is_edited_flag else ""
                    expander_label = f"{p_icon} **{task.task_title}**{edited_label}"
                    
                    with st.expander(expander_label, expanded=False):
                        st.markdown(f"**Description:**\n{task.task_description or '*No description provided.*'}")
                        st.markdown(f"**Priority:** {p_icon} {p_name} ({age_days}d pending)")
                        st.markdown(
                            f"<small style='color: grey;'>Created by: {task.created_by} on {task.created_datetime.strftime('%Y-%m-%d %H:%M')}</small>", 
                            unsafe_allow_html=True
                        )
                        if task.edited_by:
                            st.markdown(
                                f"<small style='color: grey;'>Last edited by: {task.edited_by} on {task.edited_datetime.strftime('%Y-%m-%d %H:%M')}</small>", 
                                unsafe_allow_html=True
                            )
                        
                        st.markdown("---")
                        
                        # Inline operations for each pending task
                        op_col1, op_col2 = st.columns(2)
                        
                        with op_col1:
                            if st.button("Mark as Complete", key=f"comp_{task.task_id}", use_container_width=True):
                                database.complete_task(task.task_id, st.session_state.current_user)
                                st.success("Task completed!")
                                st.rerun()
                                
                        with op_col2:
                            # Trigger Edit form visibility for this specific task
                            edit_expanded = st.toggle("Edit Task Fields", key=f"toggle_edit_{task.task_id}")
                            
                        if st.session_state.get(f"show_success_edit_{task.task_id}"):
                            st.success("Changes saved!")
                            del st.session_state[f"show_success_edit_{task.task_id}"]

                        if edit_expanded:
                            with st.form(key=f"edit_form_{task.task_id}"):
                                new_title = st.text_input("Task Title", value=task.task_title, key=f"edit_title_{task.task_id}")
                                new_description = st.text_area("Task Description", value=task.task_description or "", key=f"edit_desc_{task.task_id}")
                                submit_edit = st.form_submit_button("Save Changes", use_container_width=True, on_click=save_task_changes, args=(task.task_id,))
                                        
        # RIGHT COLUMN: Completed Tasks (Locked Permanently)
        with col_right:
            st.markdown("### ✅ Completed Tasks (Locked)")
            if not completed_tasks:
                st.info("No completed tasks yet. Mark tasks as complete to archive them.")
            else:
                for idx, task in enumerate(completed_tasks):
                    edited_label = " :green-background[Edited]" if task.is_edited_flag else ""
                    expander_label = f"🔒 **{task.task_title}**{edited_label}"
                    
                    with st.expander(expander_label, expanded=False):
                        st.markdown(f"**Description:**\n{task.task_description or '*No description provided.*'}")
                        
                        # Complete historical record metadata
                        st.markdown(
                            f"""
                            <div style='background: rgba(16, 185, 129, 0.05); padding: 10px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.1); margin-top: 10px;'>
                                <p style='margin:0; font-size:0.8rem; color:#065F46;'>
                                    <b>Completed By:</b> {task.completed_by}<br>
                                    <b>Completion Date:</b> {task.completed_datetime.strftime('%Y-%m-%d') if task.completed_datetime else ''}<br>
                                    <b>Completion Time:</b> {task.completed_datetime.strftime('%H:%M:%S') if task.completed_datetime else ''}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        st.markdown(
                            f"""
                            <p style='margin-top:10px; margin-bottom:0; font-size:0.75rem; color:grey;'>
                                Created by {task.created_by} on {task.created_datetime.strftime('%Y-%m-%d %H:%M')}<br>
                                {'Edited by ' + task.edited_by + ' on ' + task.edited_datetime.strftime('%Y-%m-%d %H:%M') if task.edited_by else ''}
                            </p>
                            """,
                            unsafe_allow_html=True
                        )
# Tab 2: Create New Task
with tab_create:
    st.markdown("### ➕ Create New Task")
    
    if st.session_state.get("show_success_task"):
        st.markdown(
            """
            <div class="checkmark-wrapper">
              <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none"/>
                <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
              </svg>
            </div>
            <style>
            .checkmark-wrapper {
              display: flex;
              justify-content: center;
              align-items: center;
              margin-top: 10px;
              margin-bottom: 20px;
            }
            .checkmark {
              width: 60px;
              height: 60px;
              border-radius: 50%;
              display: block;
              stroke-width: 3;
              stroke: #fff;
              stroke-miterlimit: 10;
              box-shadow: inset 0px 0px 0px #10B981;
              animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s forwards;
            }
            .checkmark__circle {
              stroke-dasharray: 166;
              stroke-dashoffset: 166;
              stroke-width: 3;
              stroke-miterlimit: 10;
              stroke: #10B981;
              fill: none;
              animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
            }
            .checkmark__check {
              transform-origin: 50% 50%;
              stroke-dasharray: 48;
              stroke-dashoffset: 48;
              animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
            }
            @keyframes stroke {
              100% {
                stroke-dashoffset: 0;
              }
            }
            @keyframes scale {
              0%, 100% {
                transform: none;
              }
              50% {
                transform: scale3d(1.1, 1.1, 1);
              }
            }
            @keyframes fill {
              100% {
                box-shadow: inset 0px 0px 0px 40px #10B981;
              }
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.success(f"Successfully created task: '{st.session_state.show_success_task}'!")
        st.session_state.show_success_task = ""
        
    with st.form(key="create_task_form", clear_on_submit=True):
        title = st.text_input("Task Title *", placeholder="Enter the title or summary of the task")
        desc = st.text_area("Task Description", placeholder="Enter full details and guidelines for the task...")
        submit_btn = st.form_submit_button("Add Task to Workspace", use_container_width=True)
        
        if submit_btn:
            title_stripped = title.strip()
            desc_stripped = desc.strip()
            if not title_stripped:
                st.error("Task Title is mandatory.")
            else:
                database.create_task(
                    title=title_stripped,
                    description=desc_stripped,
                    created_by=st.session_state.current_user
                )
                st.session_state.show_success_task = title_stripped
                st.rerun()
