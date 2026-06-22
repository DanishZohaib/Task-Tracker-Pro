import os
import database
from datetime import datetime

def test_workflow():
    print("Initializing Database...")
    database.init_db()
    
    # NEW: Test OTP and Mobile features on User Registration
    print("Testing User Registration with Mobile and OTP...")
    user_mobile = "+1234567890"
    user_otp = database.create_user("OTP User", "pass123", full_name="OTP FullName", mobile_number=user_mobile)
    assert user_otp is not None, "Failed to create user with mobile"
    assert user_otp.is_verified is False, "New user with mobile should not be verified yet"
    assert user_otp.full_name == "OTP FullName", "Full name was not set"
    assert user_otp.mobile_number == user_mobile, "Mobile number was not set"
    print("Success: New user created with mobile number in pending state.")
    
    # Test mobile uniqueness
    try:
        database.create_user("Another User", "pass123", full_name="Another", mobile_number=user_mobile)
        assert False, "Should have raised ValueError for duplicate mobile"
    except ValueError as ve:
        print(f"Success: Unique mobile constraint raised expected error: {ve}")
        
    # Test OTP set and verification
    from datetime import datetime, timedelta
    print("Testing OTP Assignment & Verification...")
    import otp_service
    otp_code = otp_service.generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=10)
    database.update_user_otp("OTP User", otp_code, expiry)
    
    # Verify incorrect OTP fails
    assert database.verify_user_otp("OTP User", "000000") is False, "Verification should fail with wrong OTP"
    
    # Verify correct OTP succeeds
    assert database.verify_user_otp("OTP User", otp_code) is True, "Verification failed with correct OTP"
    
    # Verify OTP is wiped after use (prevent reuse)
    db_user = database.get_user_by_name("OTP User")
    assert db_user.is_verified is True, "User should be marked verified now"
    assert db_user.otp_code is None, "OTP code should be cleared after verification"
    print("Success: OTP verification and prevention of reuse verified.")
    
    # Test OTP Expiry
    print("Testing OTP Expiry...")
    expired_otp = "888888"
    past_expiry = datetime.utcnow() - timedelta(minutes=1)
    database.update_user_otp("OTP User", expired_otp, past_expiry)
    assert database.verify_user_otp("OTP User", expired_otp) is False, "Expired OTP should fail verification"
    print("Success: Expired OTP was rejected.")
    
    # Test Password Reset via OTP helper
    print("Testing Password Reset via Mobile OTP...")
    found_by_mobile = database.get_user_by_mobile(user_mobile)
    assert found_by_mobile is not None, "User should be lookupable by mobile"
    assert found_by_mobile.user_name == "OTP User", "User name mismatch by mobile lookup"
    
    reset_success = database.update_user_password("OTP User", "newsecret999")
    assert reset_success is True, "Failed to reset password"
    assert database.verify_user("OTP User", "newsecret999") is True, "Failed to authenticate with new password"
    print("Success: Password reset via OTP verified.")

    # 1. Create a user (legacy backwards compatibility)
    print("Testing Legacy User Registration (Backward Compatibility)...")
    user = database.create_user("Test Danish Zohaib", "password123")
    assert user is not None, "Failed to create user"
    assert user.is_verified is True, "Legacy user without mobile should be auto-verified"
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
    
    # 7. Verify Admin and Role-Based features
    print("Verifying Admin Seeding & Helpers...")
    admin = database.get_user_by_name("admin")
    assert admin is not None, "Admin user not seeded"
    assert admin.role == "admin", "Admin role not correct"
    assert admin.is_active is True, "Admin should be active"
    assert admin.is_verified is True, "Admin should be verified"
    assert database.verify_user("admin", "adminpassword") is True, "Failed to login as admin"
    print("Success: Default admin seeded and verified.")

    print("Verifying Account Deactivation & Status...")
    # Deactivate OTP User
    assert database.update_user_status("OTP User", False) is True, "Failed to deactivate user"
    deactivated = database.get_user_by_name("OTP User")
    assert deactivated.is_active is False, "User is_active did not change to False"
    
    # Activate back
    assert database.update_user_status("OTP User", True) is True, "Failed to activate user"
    activated = database.get_user_by_name("OTP User")
    assert activated.is_active is True, "User is_active did not change to True"
    print("Success: User activation/deactivation toggling verified.")

    print("Verifying Admin Password Override...")
    # Admin resets password for OTP User
    assert database.admin_reset_password("OTP User", "adminoverrider") is True, "Failed password override"
    assert database.verify_user("OTP User", "adminoverrider") is True, "Password reset override failed to verify"
    print("Success: Admin password reset override verified.")
    
    print("\nALL FUNCTIONAL DATABASE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    # Remove old database if exists to start fresh
    if os.path.exists("tasktracker.db"):
        try:
            os.remove("tasktracker.db")
        except PermissionError:
            try:
                from database import Base, engine
                Base.metadata.drop_all(bind=engine)
                print("Database locked by another process. Dropped all tables to clean instead.")
            except Exception as cleanup_err:
                print(f"Clean up warning: {cleanup_err}")
    test_workflow()
