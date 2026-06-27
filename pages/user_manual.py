import streamlit as st

if "current_user" not in st.session_state or st.session_state.current_user is None:
    st.warning("Please log in to access this page.")
    st.stop()

from components.custom_styles import inject_custom_css
from config import FOOTER_CREATOR

inject_custom_css()

st.title("📖 User Manual & Reference Guide")
st.write("Welcome to the official user guide for TaskTracker Pro.")

st.markdown("---")

# Sections with expanders for clean presentation
with st.expander("1. Application Overview", expanded=True):
    st.markdown(
        """
        **TaskTracker Pro** is a modern, multi-user task management application designed for tracking team collaborations and auditing daily achievements.
        
        **Key Architectural Highlights:**
        - **Multi-User Collaboration:** Identifies every operation (creation, edits, closures) by individual username.
        - **Data Integrity:** Employs a local SQLite engine to store persistent details and prevent records deletion.
        - **Automatic Aging Priorities:** Automatically flags tasks according to their date of creation, signaling how long actions have been outstanding.
        """
    )

with st.expander("2. How to Create Tasks"):
    st.markdown(
        """
        1. Navigate to the **Task Manager** page from the sidebar menu.
        2. Click on the **Create New Task** tab.
        3. Fill in the **Task Title** (required) and a detailed **Task Description** (optional).
        4. Click **Add Task to Workspace**.
        
        *Note: The task is automatically logged as 'Pending' with normal priority, and your name is captured as the creator.*
        """
    )

with st.expander("3. How to Edit Tasks"):
    st.markdown(
        """
        1. Navigate to the **Task Manager** page and locate the task under the **Pending Tasks** list.
        2. Expand the task details card and check the **Edit Task Fields** toggle.
        3. A form will appear allowing you to modify the title or description.
        4. Edit the fields and click **Save Changes**.
        
        *Note: The task will now show a green **[Edited]** label. Only pending tasks can be edited.*
        """
    )

with st.expander("4. How to Complete Tasks"):
    st.markdown(
        """
        1. Navigate to the **Task Manager** page and look at your **Pending Tasks**.
        2. Expand the task you wish to close and click **Mark as Complete**.
        3. The system will log your name and timestamp, archive the task, and permanently lock it.
        
        > [!WARNING]
        > Completed tasks are locked permanently. They cannot be edited or modified.
        """
    )

with st.expander("5. Dashboard Explanation"):
    st.markdown(
        """
        The **Payroll Dashboard** page aggregates real-time metrics across 4 custom visual charts:
        
        - **Monthly Task Trend:** Groups task creation and completion by calendar month to show performance velocity.
        - **Task Completion Status:** Displays a pie/donut representation of pending vs. completed tasks.
        - **User Performance:** Measures how many tasks have been initiated and closed by each specific profile.
        - **Productivity Trend:** Plots task completion frequency to track monthly progress.
        """
    )

with st.expander("6. Reports & Export Features"):
    st.markdown(
        """
        You can export logs and payroll tasks summaries at any time:
        - Go to the **Payroll Tasks Summary** page to download full workbook logs (Excel, CSV) or formatted summary dossiers (PDF).
        - Go to the **Audit Trail** page to filter specific intervals, usernames, or actions, and export that filtered view.
        """
    )

with st.expander("7. Audit Trail Explanation"):
    st.markdown(
        """
        The **Audit Trail** page logs all transactions. Every row records:
        - **Log ID & Timestamp:** When the event occurred.
        - **Action:** 'CREATE', 'EDIT', or 'COMPLETE'.
        - **User:** The name of the profile who initiated the change.
        - **Details:** Textual summary of what was altered (e.g. title changes).
        """
    )

with st.expander("8. Frequently Asked Questions (FAQ)"):
    st.markdown(
        """
        **Q: How do I change my active profile?**
        - A: Use the **Logout / Switch User** button in the sidebar to return to the landing screen and choose or register a different profile.
        
        **Q: Can I delete a task?**
        - A: No. To preserve full audit trail compliance and historical data integrity, task deletion is not allowed. Completed tasks are archived and locked.
        
        **Q: What determines task priority?**
        - A: Priority is calculated automatically based on how long a pending task has been open:
          - 🟢 **Normal**: < 3 days old
          - 🟡 **Medium**: 3 to 7 days old
          - 🔴 **High (Overdue)**: &ge; 7 days old
        """
    )

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style='text-align: center; color: #94A3B8; font-size: 0.8rem; border-top: 1px solid #E2E8F0; padding-top: 15px;'>
        Designed & Conceptualized by {FOOTER_CREATOR} | TaskTracker Pro &copy; 2026
    </div>
    """,
    unsafe_allow_html=True
)
