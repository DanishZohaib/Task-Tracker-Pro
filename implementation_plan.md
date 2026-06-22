# Implementation Plan: Username-Only Auth + Admin Control Panel + OTP Support

This plan details the changes required to remove all email references, switch to username-only login, introduce the Admin role with account activation control, password override, manual OTP generation, and build an interactive Admin Control Panel page.

## User Review Required

> [!IMPORTANT]
> **Admin Seeding Strategy**:
> We will auto-seed a default administrator account in `database.py` during initialization:
> - **Username**: `admin`
> - **Password**: `adminpassword237`
> - **Mobile Number**: `+923003712150`
> - **Role**: `admin`
> - **Verification Status**: `is_verified = True`
> - **Account Status**: `is_active = True`
>
> **Existing User Role Migration**:
> All existing database users will default to the `"user"` role. Any user with a `NULL` `is_active` status will be set to `True` (active) by default.

## Proposed Changes

---

### Database Layer

#### [MODIFY] [database.py](file:///e:/Antigravity/Task-Tracker-Pro/database.py)
- **Model Modifications**:
  - Update `User` class to ensure `role` (default `"user"`) and `is_active` (default `True`) are defined:
    ```python
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    ```
- **Automatic Migration & Seeding**:
  - Update `init_db()` to dynamically add `role` and `is_active` columns using `ALTER TABLE`.
  - In `init_db()`, seed the default admin account:
    - Username: `admin`, Password: `adminpassword`, Mobile: `+15550199`, Role: `admin`, is_verified: `True`, is_active: `True`.
  - Perform data updates for existing users:
    - Set `role = 'user'` where role is null.
    - Set `is_active = 1` where is_active is null.
- **Helper Functions**:
  - Update `verify_user(username, password)` to also check that `is_active` is True.
  - Add admin action helper functions:
    - `get_all_users() -> List[User]`: Fetches all registered users for the Admin panel.
    - `update_user_status(username: str, is_active: bool)`: Activates or deactivates an account.
    - `update_user_role(username: str, role: str)`: Toggles user/admin roles.
    - `admin_reset_password(username: str, new_password_raw: str)`: Allows admin to manually override a password securely.

---

### Streamlit UI Layer

#### [MODIFY] [app.py](file:///e:/Antigravity/Task-Tracker-Pro/app.py)
- **Email Field Removal**:
  - Change all registration UI labels and inputs from "Username / Email" to **"Username"**.
  - Adjust placeholder text in `app.py` registration text input.
- **Login Block for Deactivated Users**:
  - Update credentials verification logic: if the user's `is_active` column in the database is `False`, block login with the error: `"Your account has been deactivated. Please contact an administrator."`
- **Dynamic Admin Navigation**:
  - If the currently logged-in user is an admin (`user_obj.role == 'admin'`), dynamically add the new **Admin Control Panel** page to the Streamlit navigation panel.

---

### Admin Module

#### [NEW] [pages/admin_panel.py](file:///e:/Antigravity/Task-Tracker-Pro/pages/admin_panel.py)
- Build an interactive administration portal accessible only by Admin users:
  - **Overview Cards**: Show aggregate statistics (total users, active vs inactive, verified counts).
  - **User Management Table**:
    - List all users dynamically.
    - Add control actions: Activate/Deactivate, change role, and manually override password.
  - **Manual OTP Support Tool**:
    - Search field (by username or mobile number).
    - Generate OTP button: Generates a 6-digit OTP code (5-10 min expiry) and saves it to the database.
    - Display OTP code on screen for verbal assistance.
    - Provide a secondary button to send it via mock SMS gateway manually.

---

### Verification and Regression Testing

#### [MODIFY] [test_db.py](file:///e:/Antigravity/Task-Tracker-Pro/test_db.py)
- Update unit tests to cover admin seeding, account status toggling, admin password resets, role validation, and login blocking for inactive users.

## Verification Plan

### Automated Tests
- Run `python test_db.py` to verify that DB helpers, admin overrides, role controls, and active-status checks function perfectly.

### Manual Verification
1. **Admin Panel Access**:
   - Log in with the default admin account: `admin` / `adminpassword`.
   - Verify that the "Admin Control Panel" option is visible in the sidebar.
2. **Deactivation Flow**:
   - In the Admin Panel, deactivate a test user.
   - Log out, try to enter as that user, and verify that the system blocks login.
3. **Manual Password Reset Override**:
   - In the Admin Panel, override the deactivated user's password, activate them, and confirm they can log in using the admin's overridden password.
4. **OTP Support Assistance**:
   - Search for a user. Click "Generate OTP".
   - Verify that the OTP is shown on screen and matches the OTP in the database.
   - Log in as that user and verify using the admin-shared OTP.
