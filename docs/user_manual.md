# User Manual & Reference Guide - TaskTracker Pro
> **Track. Monitor. Complete.**

Welcome to the TaskTracker Pro user guide. This manual provides step-by-step instructions on navigating and utilizing all features of the application.

**Application Idea By:** Danish Zohaib

---

## 1. Application Overview

TaskTracker Pro is a responsive, multi-user task management application designed to organize, monitor, and audit daily operations. Built with a local SQLite database, the system captures a full chronological audit trail of all team interactions.

---

## 2. Navigating the Interface

Use the **Sidebar Navigation** to switch between different workspaces:
1. **Performance & Stats:**
   - **Payroll Dashboard:** Visual charts, metrics, and list of oldest pending work.
   - **Payroll Tasks Summary:** Overall workloads, top users, monthly historical records, and report downloads (PDF/Excel/CSV).
2. **Task Management:**
   - **Task Manager:** Create new tasks, update pending actions, and close completed items.
   - **Audit Trail:** Comprehensive transaction logger with date, user, and keyword search filters.
3. **Standard Guidelines:**
   - **SOP Compliance:** Professional instructions on task lifecycle regulations.
   - **User Manual:** Direct help guides and answers to FAQs.

---

## 3. Step-by-Step Instructions

### 3.1 Profile Login/Selection
1. **Register/Login:** Start the application. You must register an account (Name + Password) on the landing page, or select an existing user and authenticate with your password.
2. **Access Profile:** Once logged in, your session is tied to your name and unique numerical ID, which will be permanently recorded on every action you take for accountability.
3. To switch profiles or logout, use the **Logout / Switch User** button in the sidebar.

### 3.2 Task Creation
1. Go to the **Task Manager** page from the sidebar menu.
2. Select the **Create New Task** tab.
3. Type the **Task Title** (required) and optional **Task Description**.
4. Click **Add Task to Workspace**. The task is saved in the database as `'Pending'`.

### 3.3 Task Modification (Pending Only)
1. Go to the **Task Manager** page and view the **Pending Tasks** list.
2. Select the task expander card you wish to edit and check the **Edit Task Fields** toggle.
3. Modify the title or description inside the form.
4. Click **Save Changes**. The task will now display a green **[Edited]** tag.

### 3.4 Task Completion & Locking
1. Expand the target pending task and click **Mark as Complete**.
2. The task is moved to **Completed Tasks**, the completion timestamp is saved, and the task is permanently locked from any further modification or deletion.

### 3.5 Chart Operations (Dashboard)
- **Monthly Task Trend:** Compares monthly task creation against completions.
- **Task Completion Status:** Displays proportion of completed vs. pending tasks.
- **User Performance:** Measures counts of created/completed tasks by user name.
- **Productivity Trend:** Chronological timeline tracking monthly completions.

### 3.6 Reports Export
- Download report documents (PDF, Excel, CSV) from the **Payroll Tasks Summary** page.
- Apply filters on the **Audit Trail** page to export specific dates, users, or keywords.

---

## 4. Frequently Asked Questions (FAQ)

**Q: Can I delete a task that was created by mistake?**  
A: No. To maintain absolute compliance and full audit tracking, task deletion is disabled. If a task is no longer needed, complete it and note the status in the description, or leave it as pending.

**Q: How is task priority determined?**  
A: Priorities are calculated dynamically based on creation dates:
- 🟢 **Normal Priority**: Tasks created up to 3 days ago.
- 🟡 **Medium Priority**: Tasks created between 3 to 7 days ago.
- 🔴 **High Priority**: Overdue tasks created more than 7 days ago.

**Q: Where is my data saved?**  
A: All profiles, tasks, and audit histories are written to a persistent SQLite database (`tasktracker.db`) in your workspace.
