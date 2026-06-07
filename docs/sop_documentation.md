# Standard Operating Procedure (SOP) - TaskTracker Pro
> **Document Code:** SOP-TTP-001  
> **Version:** 1.0.0  
> **Effective Date:** June 7, 2026  
> **Author / Creator:** Danish Zohaib  

---

## 1. Purpose
This document establishes standard methods and compliance requirements for task creation, updating, completion, and transaction auditing in TaskTracker Pro. Adhering to these rules ensures data integrity and an unalterable history of operations.

---

## 2. Standard Operating Procedures

### 2.1 Task Creation Procedure
- **Trigger:** Identifying a new work item or objective.
- **Actions:**
  1. Login to TaskTracker Pro using your full name or select your profile. Anonymous creation is blocked.
  2. Access the **Task Manager** -> **Create New Task**.
  3. Enter a mandatory **Task Title** summarizing the objective.
  4. Write a descriptive **Task Description** with any necessary instructions or resources.
  5. Click **Add Task to Workspace**.
- **System Behavior:**
  - Auto-captures the login name as `Created By`.
  - Stamps creation date and time.
  - Automatically initializes priority based on age.

---

### 2.2 Task Modification Procedure (Pending Tasks Only)
- **Trigger:** Changes in parameters or details of in-progress tasks.
- **Actions:**
  1. Select the task from the **Pending Tasks** list in the **Task Manager**.
  2. Toggle **Edit Task Fields**.
  3. Modify the title or description text and click **Save Changes**.
- **Rules:**
  - Modification is strictly restricted to tasks in the `'Pending'` state.
- **System Behavior:**
  - Automatically updates `edited_by` and `edited_datetime`.
  - Sets the `is_edited_flag` to true.
  - Generates a green **[Edited]** tag next to the task.
  - Records detailed modifications in the permanent Audit Trail.

---

### 2.3 Task Completion Procedure
- **Trigger:** Successful completion of all deliverables related to a task.
- **Actions:**
  1. Go to the **Pending Tasks** section of the **Task Manager**.
  2. Locate the specific task, expand it, and click **Mark as Complete**.
- **Rules:**
  - Once completed, the task state is permanently saved.
  - Completed tasks are permanently locked and cannot be edited, completed again, or deleted.
- **System Behavior:**
  - Saves closing timestamp and username.
  - Locks the record in the database.

---

## 3. Audit Compliance Regulations

- **Immutable Logs:** Audit trails are permanent. SQLite records cannot be deleted or pruned.
- **Signature Mandatory:** Every operation must be signed by the active user name.
- **Timestamp Integrity:** The system utilizes internal server timestamps for date/time logs to prevent manual back-dating of logs.

---

## 4. Branding & Credits
Conceptualized and designed by **Danish Zohaib**. This attribution is displayed across all pages and reports of the TaskTracker Pro system.
