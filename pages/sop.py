import streamlit as st

if "current_user" not in st.session_state or st.session_state.current_user is None:
    st.warning("Please log in to access this page.")
    st.stop()

from components.custom_styles import inject_custom_css
from config import FOOTER_CREATOR

inject_custom_css()

st.title("📋 Standard Operating Procedure (SOP)")
st.write("Mandatory guidelines for task management, audit logs compliance, and workflow integrity.")

st.markdown("---")

st.markdown("### 1. Task Creation SOP")
st.info(
    """
    **Objective:** Establish a new work item with clear tracking ownership.
    
    1. **Name Identification:** Verify that your name is correctly registered and displayed in the sidebar. This acts as your audit signature.
    2. **Task Title:** Enter a concise, action-oriented title (e.g., *'Review Q2 Marketing Report'* rather than *'Marketing'*).
    3. **Task Description:** Input sufficient context, requirements, links, or sub-tasks to ensure another team member can understand the work.
    4. **Priority Calculation:** The system will automatically compute priority based on creation timestamp:
       - Normal Priority (Green 🟢): Freshly created, up to 3 days old.
       - Medium Priority (Yellow 🟡): 3 to 7 days old.
       - High Priority (Red 🔴): Older than 7 days (requires urgent management action).
    """
)

st.markdown("### 2. Task Update SOP")
st.warning(
    """
    **Objective:** Modify details of in-progress tasks while maintaining change history.
    
    1. **Eligibility:** Editing is **only** permitted on **Pending** tasks. Once completed, a task cannot be modified.
    2. **Editing Flow:** Locate the task under the *Pending Tasks* list, expand it, toggle 'Edit Task Fields', perform modifications in the title or description, and click 'Save Changes'.
    3. **Audit Tracking:** The system will:
       - Save the editor username and edit timestamp.
       - Set the `is_edited_flag` to true.
       - Display a visible green label **[Edited]** next to the task.
       - Log the precise details of the edit (e.g. what fields were modified) in the permanent Audit Trail.
    """
)

st.markdown("### 3. Task Completion SOP")
st.success(
    """
    **Objective:** Formally close a task and lock the historical record.
    
    1. **Review:** Ensure all deliverables for the task are complete.
    2. **Closure Action:** Click the *Mark as Complete* button.
    3. **Archiving & Permanent Lock:** The task is instantly locked. 
       - It is moved to the *Completed Tasks* section.
       - It cannot be edited, deleted, or modified.
       - The completion timestamp, date, and closing user are permanently hard-coded.
    """
)

st.markdown("### 4. Audit Compliance SOP")
st.markdown(
    """
    > [!IMPORTANT]
    > **Audit Regulations for TaskTracker Pro:**
    > 
    > - **Authentication Security:** Users must authenticate using their registered username and password to access the workspace.
    > - **Audit Trail Immutability:** No user, administrator, or manager has permission to delete, wipe, or truncate audit logs or tasks once written.
    > - **Strict Accountability:** Every action (creation, modification, completion) permanently records the user's name and numerical User ID.
    > - **Mandatory Signatures:** Every log entry must register the active user profile and action timestamp.
    > - **Data Retention:** All records are written to a permanent SQLite database (`tasktracker.db`) for full compliance auditing.
    """
)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style='background-color: #F8FAFC; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0; text-align: center;'>
        <small style='color: #475569;'>
            <b>TaskTracker Pro SOP</b><br>
            <b>{FOOTER_CREATOR}</b><br>
            Compliance Standard: V1.0.0
        </small>
    </div>
    """,
    unsafe_allow_html=True
)
