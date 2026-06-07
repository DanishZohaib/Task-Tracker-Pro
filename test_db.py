import os
import database
from datetime import datetime

def test_workflow():
    print("Initializing Database...")
    database.init_db()
    
    # 1. Create a user
    print("Testing User Registration...")
    user = database.create_user("Test Danish Zohaib", "password123")
    assert user is not None, "Failed to create user"
    print(f"Success: Registered user ID {user.user_id} - '{user.user_name}'")
    
    # 2. Create a task
    print("Testing Task Creation...")
    task = database.create_task(
        title="Test Task Title",
        description="Verify this description is logged correctly",
        created_by="Test Danish Zohaib"
    )
    assert task is not None, "Failed to create task"
    assert task.status == "Pending", "Initial task status must be Pending"
    assert task.is_edited_flag is False, "Initial task must not be marked as edited"
    print(f"Success: Created Task ID {task.task_id} - '{task.task_title}'")
    
    # 3. Edit task
    print("Testing Task Editing...")
    edited_task = database.edit_task(
        task_id=task.task_id,
        title="Updated Task Title",
        description="Verify description edit is logged",
        edited_by="Test Danish Zohaib"
    )
    assert edited_task is not None, "Failed to edit task"
    assert edited_task.task_title == "Updated Task Title", "Task title did not update"
    assert edited_task.is_edited_flag is True, "Task is_edited_flag was not set to True"
    print("Success: Edited Task title and description")
    
    # 4. Complete task
    print("Testing Task Completion...")
    completed_task = database.complete_task(
        task_id=task.task_id,
        completed_by="Test Danish Zohaib"
    )
    assert completed_task is not None, "Failed to complete task"
    assert completed_task.status == "Completed", "Task status did not change to Completed"
    assert completed_task.completed_by == "Test Danish Zohaib", "Completed by user mismatch"
    print("Success: Completed Task and marked locked")
    
    # 5. Verify edit lock
    print("Testing Task Locking Rules...")
    failed_edit = database.edit_task(
        task_id=task.task_id,
        title="Attempt to change locked task",
        description="This edit should fail",
        edited_by="Test Danish Zohaib"
    )
    assert failed_edit is None, "Modification allowed on a completed, locked task!"
    print("Success: Lock verified. Completed task cannot be modified.")
    
    # 6. Verify audit logs
    print("Verifying Audit Logs...")
    logs = database.get_audit_logs()
    assert len(logs) >= 3, "Audit logs count does not match operations (CREATE, EDIT, COMPLETE)"
    
    actions = [l.action_type for l in logs]
    assert "CREATE" in actions, "CREATE action not logged"
    assert "EDIT" in actions, "EDIT action not logged"
    assert "COMPLETE" in actions, "COMPLETE action not logged"
    print("Success: Permanent audit trail verified.")
    
    print("\nALL FUNCTIONAL DATABASE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    # Remove old database if exists to start fresh
    if os.path.exists("tasktracker.db"):
        os.remove("tasktracker.db")
    test_workflow()
