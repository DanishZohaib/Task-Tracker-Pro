import streamlit as st
import database
import otp_service
from components.custom_styles import inject_custom_css, draw_footer

# Initialize database schema
database.init_db()

st.set_page_config(
    page_title="TaskTracker Pro",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply customized styles
inject_custom_css()

# Session State Initialization
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_step" not in st.session_state:
    st.session_state.auth_step = "login"
if "temp_verify_username" not in st.session_state:
    st.session_state.temp_verify_username = None
if "temp_reset_mobile" not in st.session_state:
    st.session_state.temp_reset_mobile = None

# Fetch all users
users = database.get_users()
user_list = [u.user_name for u in users]

# Left side branding header & Developer Helper (rendered only when logged out)
if st.session_state.current_user is None:
    st.sidebar.markdown(f"# 📋 TaskTracker Pro")
    st.sidebar.markdown("`Track. Monitor. Complete.`")
    st.sidebar.markdown("---")
    
    # Developer OTP Assist Box
    pending_user = None
    if st.session_state.auth_step in ["verify_registration_otp", "verify_login_otp"] and st.session_state.temp_verify_username:
        pending_user = database.get_user_by_name(st.session_state.temp_verify_username)
    elif st.session_state.auth_step == "forgot_password_verify" and st.session_state.temp_reset_mobile:
        pending_user = database.get_user_by_mobile(st.session_state.temp_reset_mobile)
        
    if pending_user and pending_user.otp_code:
        st.sidebar.info(
            f"🔧 **Developer Helper**\n\n"
            f"Latest OTP for **{pending_user.user_name}**:\n"
            f"## `{pending_user.otp_code}`\n"
            f"*(Sent mock SMS to {pending_user.mobile_number})*"
        )

if st.session_state.current_user is None:
    # Beautiful landing / registration / verification page
    st.markdown("<h1 style='text-align: center; color: #4F46E5;'>📋 TaskTracker Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #6B7280; font-weight: 400;'>Track. Monitor. Complete.</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.session_state.auth_step == "login":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(
                """
                <div style='background: rgba(79, 70, 229, 0.05); padding: 25px; border-radius: 12px; border: 1px solid rgba(79, 70, 229, 0.1);'>
                    <h4 style='margin-top:0; color: #4F46E5;'>🔑 Access Profile</h4>
                    <p style='color: #6B7280; font-size: 0.9rem;'>Select an existing user profile to load your dashboards and tasks.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if user_list:
                selected_user = st.selectbox("Select User Profile", options=["-- Select --"] + user_list)
                login_password = st.text_input("Password", type="password", key="login_pass")
                if selected_user != "-- Select --":
                    col_btn_1, col_btn_2 = st.columns([2, 1])
                    with col_btn_1:
                        if st.button("Enter Workspace", key="enter_ws_btn", use_container_width=True):
                            if database.verify_user(selected_user, login_password):
                                user_obj = database.get_user_by_name(selected_user)
                                if not user_obj.is_active:
                                    st.error("Your account has been deactivated. Please contact an administrator.")
                                elif user_obj.is_verified:
                                    st.session_state.current_user = f"{selected_user} (ID: {user_obj.user_id})"
                                    st.rerun()
                                else:
                                    # Generate OTP and require verification
                                    from datetime import datetime, timedelta
                                    otp_code = otp_service.generate_otp()
                                    expiry = datetime.utcnow() + timedelta(minutes=10)
                                    database.update_user_otp(selected_user, otp_code, expiry)
                                    otp_service.send_otp(user_obj.mobile_number, otp_code)
                                    
                                    st.session_state.temp_verify_username = selected_user
                                    st.session_state.auth_step = "verify_login_otp"
                                    st.warning("Mobile verification pending. Please verify your OTP.")
                                    st.rerun()
                            else:
                                st.error("Incorrect password.")
                    with col_btn_2:
                        if st.button("Forgot?", key="forgot_pass_btn", use_container_width=True):
                            st.session_state.auth_step = "forgot_password_request"
                            st.rerun()
            else:
                st.info("No users have been registered yet. Please register on the right to start!")
                
        with col2:
            st.markdown(
                """
                <div style='background: rgba(16, 185, 129, 0.05); padding: 25px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.1);'>
                    <h4 style='margin-top:0; color: #10B981;'>📝 Register New Profile</h4>
                    <p style='color: #6B7280; font-size: 0.9rem;'>Enter your details below to register. A verification OTP will be sent to your mobile number.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            reg_fullname = st.text_input("Full Name", placeholder="e.g. Danish Zohaib").strip()
            reg_username = st.text_input("Username", placeholder="e.g. danishz").strip()
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_mobile = st.text_input("Mobile Number", placeholder="e.g. +1234567890").strip()
            
            if st.button("Register & Verify", key="reg_enter_btn", use_container_width=True):
                if reg_fullname and reg_username and reg_password and reg_mobile:
                    # Enforce uniqueness
                    existing_username = database.get_user_by_name(reg_username)
                    existing_mobile = database.get_user_by_mobile(reg_mobile)
                    
                    if existing_username:
                        st.error("Username already exists. Please choose a different one.")
                    elif existing_mobile:
                        st.error("Mobile number is already registered by another user.")
                    else:
                        try:
                            # Create user in database (pending verification)
                            user_obj = database.create_user(
                                username=reg_username,
                                password=reg_password,
                                full_name=reg_fullname,
                                mobile_number=reg_mobile
                            )
                            # Generate and save OTP
                            from datetime import datetime, timedelta
                            otp_code = otp_service.generate_otp()
                            expiry = datetime.utcnow() + timedelta(minutes=10)
                            database.update_user_otp(reg_username, otp_code, expiry)
                            
                            # Send OTP
                            otp_service.send_otp(reg_mobile, otp_code)
                            
                            # Send Admin notification
                            otp_service.send_admin_new_registration_notification(
                                new_user_name=reg_fullname,
                                email=reg_username,
                                mobile=reg_mobile
                            )
                            
                            # Transition state
                            st.session_state.temp_verify_username = reg_username
                            st.session_state.auth_step = "verify_registration_otp"
                            st.success("Registration submitted! Please verify the OTP sent to your mobile.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error during registration: {e}")
                else:
                    st.error("All fields (Full Name, Username, Password, Mobile) are mandatory.")
                    
    elif st.session_state.auth_step in ["verify_registration_otp", "verify_login_otp"]:
        st.markdown(
            f"""
            <div style='max-width: 500px; margin: 0 auto; background: rgba(79, 70, 229, 0.05); padding: 30px; border-radius: 12px; border: 1px solid rgba(79, 70, 229, 0.15);'>
                <h3 style='margin-top:0; color: #4F46E5; text-align: center;'>🔐 Verify Mobile OTP</h3>
                <p style='color: #6B7280; font-size: 0.95rem; text-align: center;'>
                    A 6-digit OTP code has been sent to the registered mobile number for <b>{st.session_state.temp_verify_username}</b>.<br>
                    Please enter the code below to activate your account.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            otp_input = st.text_input("Enter 6-Digit OTP", max_chars=6, placeholder="e.g. 123456").strip()
            
            col_v1, col_v2 = st.columns([1, 1])
            with col_v1:
                if st.button("Verify & Login", key="verify_otp_btn", use_container_width=True):
                    if otp_input:
                        if database.verify_user_otp(st.session_state.temp_verify_username, otp_input):
                            user_obj = database.get_user_by_name(st.session_state.temp_verify_username)
                            st.session_state.current_user = f"{st.session_state.temp_verify_username} (ID: {user_obj.user_id})"
                            st.session_state.auth_step = "login"
                            st.session_state.temp_verify_username = None
                            st.success("Verification successful! Welcome to TaskTracker Pro.")
                            st.rerun()
                        else:
                            st.error("Invalid or expired OTP. Please try again.")
                    else:
                        st.error("Please enter the 6-digit OTP.")
                        
            with col_v2:
                if st.button("Cancel / Back", key="verify_cancel_btn", use_container_width=True):
                    st.session_state.auth_step = "login"
                    st.session_state.temp_verify_username = None
                    st.rerun()
            
            st.markdown("---")
            if st.button("🔄 Resend OTP", key="resend_otp_btn", use_container_width=True):
                user_obj = database.get_user_by_name(st.session_state.temp_verify_username)
                if user_obj:
                    from datetime import datetime, timedelta
                    otp_code = otp_service.generate_otp()
                    expiry = datetime.utcnow() + timedelta(minutes=10)
                    database.update_user_otp(user_obj.user_name, otp_code, expiry)
                    otp_service.send_otp(user_obj.mobile_number, otp_code)
                    st.toast("A new OTP has been sent!")
                    st.rerun()

    elif st.session_state.auth_step == "forgot_password_request":
        st.markdown(
            f"""
            <div style='max-width: 500px; margin: 0 auto; background: rgba(245, 158, 11, 0.05); padding: 30px; border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.15);'>
                <h3 style='margin-top:0; color: #F59E0B; text-align: center;'>🔁 Forgot Password</h3>
                <p style='color: #6B7280; font-size: 0.95rem; text-align: center;'>
                    Enter your registered mobile number below. We will send you an OTP to reset your password safely.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_fp1, col_fp2, col_fp3 = st.columns([1, 2, 1])
        with col_fp2:
            fp_mobile = st.text_input("Registered Mobile Number", placeholder="e.g. +1234567890").strip()
            
            col_v1, col_v2 = st.columns([1, 1])
            with col_v1:
                if st.button("Send Reset OTP", key="send_reset_otp_btn", use_container_width=True):
                    if fp_mobile:
                        user_obj = database.get_user_by_mobile(fp_mobile)
                        if user_obj:
                            # Generate and save OTP
                            from datetime import datetime, timedelta
                            otp_code = otp_service.generate_otp()
                            expiry = datetime.utcnow() + timedelta(minutes=10)
                            database.update_user_otp(user_obj.user_name, otp_code, expiry)
                            
                            # Send OTP
                            otp_service.send_otp(user_obj.mobile_number, otp_code)
                            
                            st.session_state.temp_reset_mobile = fp_mobile
                            st.session_state.auth_step = "forgot_password_verify"
                            st.success("OTP sent! Please enter the code and your new password.")
                            st.rerun()
                        else:
                            st.error("No account found registered with this mobile number.")
                    else:
                        st.error("Please enter your registered mobile number.")
                        
            with col_v2:
                if st.button("Back to Login", key="fp_cancel_btn", use_container_width=True):
                    st.session_state.auth_step = "login"
                    st.session_state.temp_reset_mobile = None
                    st.rerun()

    elif st.session_state.auth_step == "forgot_password_verify":
        st.markdown(
            f"""
            <div style='max-width: 500px; margin: 0 auto; background: rgba(245, 158, 11, 0.05); padding: 30px; border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.15);'>
                <h3 style='margin-top:0; color: #F59E0B; text-align: center;'>🔁 Reset Password</h3>
                <p style='color: #6B7280; font-size: 0.95rem; text-align: center;'>
                    An OTP code has been sent to your mobile: <b>{st.session_state.temp_reset_mobile}</b>.<br>
                    Enter the code along with your new password below.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_fpv1, col_fpv2, col_fpv3 = st.columns([1, 2, 1])
        with col_fpv2:
            fpv_otp = st.text_input("Enter 6-Digit OTP", max_chars=6, placeholder="e.g. 123456").strip()
            new_pass1 = st.text_input("New Password", type="password", key="fpv_pass1")
            new_pass2 = st.text_input("Confirm New Password", type="password", key="fpv_pass2")
            
            col_v1, col_v2 = st.columns([1, 1])
            with col_v1:
                if st.button("Reset Password", key="reset_pass_btn", use_container_width=True):
                    if fpv_otp and new_pass1 and new_pass2:
                        if new_pass1 != new_pass2:
                            st.error("Passwords do not match.")
                        else:
                            # Verify OTP first
                            user_obj = database.get_user_by_mobile(st.session_state.temp_reset_mobile)
                            if user_obj:
                                if database.verify_user_otp(user_obj.user_name, fpv_otp):
                                    # Update password
                                    database.update_user_password(user_obj.user_name, new_pass1)
                                    st.session_state.auth_step = "login"
                                    st.session_state.temp_reset_mobile = None
                                    st.success("Password reset successfully! Please log in.")
                                    st.rerun()
                                else:
                                    st.error("Invalid or expired OTP.")
                            else:
                                st.error("Account not found.")
                    else:
                        st.error("All fields (OTP, Password, Confirm Password) are mandatory.")
                        
            with col_v2:
                if st.button("Cancel", key="fpv_cancel_btn", use_container_width=True):
                    st.session_state.auth_step = "login"
                    st.session_state.temp_reset_mobile = None
                    st.rerun()
            
            st.markdown("---")
            if st.button("🔄 Resend OTP", key="fpv_resend_otp_btn", use_container_width=True):
                user_obj = database.get_user_by_mobile(st.session_state.temp_reset_mobile)
                if user_obj:
                    from datetime import datetime, timedelta
                    otp_code = otp_service.generate_otp()
                    expiry = datetime.utcnow() + timedelta(minutes=10)
                    database.update_user_otp(user_obj.user_name, otp_code, expiry)
                    otp_service.send_otp(user_obj.mobile_number, otp_code)
                    st.toast("A new OTP has been sent!")
                    st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; color: #94A3B8; font-size: 0.9rem; border-top: 1px solid #E2E8F0; padding-top: 20px;'>
            Designed & Conceptualized by Danish Zohaib | TaskTracker Pro &copy; 2026
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Sidebar user details at the top of the menu
    user_str = st.session_state.current_user
    if " (ID: " in user_str:
        user_name, user_id_part = user_str.split(" (ID: ")
        user_id = user_id_part.rstrip(")")
    else:
        user_name = user_str
        user_id = ""
        
    st.sidebar.markdown(
        f"""
        <div class="user-card">
          <div class="user-avatar">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="url(#user-grad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;">
              <defs>
                <linearGradient id="user-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#4F46E5;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:1" />
                </linearGradient>
              </defs>
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div class="user-details">
            <span class="user-label">Active Session</span>
            <span class="user-name">{user_name}</span>
            <span class="user-id">ID: {user_id}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.sidebar.button("Logout / Switch User", use_container_width=True, key="logout_btn"):
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.markdown("<hr class='sidebar-divider' style='margin: 10px 0 20px 0; border: none; border-top: 1px solid rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
    
    # Navigation mapping using Streamlit Pages
    dashboard_page = st.Page("pages/dashboard.py", title="Payroll Dashboard", icon="📊", default=True)
    tasks_page = st.Page("pages/tasks.py", title="Task Manager", icon="📝")
    summary_page = st.Page("pages/payroll_tasks_summary.py", title="Payroll Tasks Summary", icon="📈")
    audit_page = st.Page("pages/audit_trail.py", title="Audit Trail", icon="🔒")
    sop_page = st.Page("pages/sop.py", title="SOP Compliance", icon="📋")
    manual_page = st.Page("pages/user_manual.py", title="User Manual", icon="📖")

    # Dynamic navigation sections
    nav_sections = {
        "Performance & Stats": [dashboard_page, summary_page],
        "Task Management": [tasks_page, audit_page],
        "Standard Guidelines": [sop_page, manual_page]
    }
    
    # Render Admin Panel if the logged-in user has admin role
    user_obj = database.get_user_by_name(user_name)
    if user_obj and user_obj.role == "admin":
        admin_page = st.Page("pages/admin_panel.py", title="Admin Control Panel", icon="🛠️")
        nav_sections["Admin Controls"] = [admin_page]

    pg = st.navigation(nav_sections)
    pg.run()
    
    # Sidebar branding header at the bottom of the menu
    st.sidebar.markdown(
        """
        <div class="sidebar-branding">
          <div class="branding-title">📋 TaskTracker Pro</div>
          <div class="branding-tagline">Track. Monitor. Complete.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    draw_footer()
