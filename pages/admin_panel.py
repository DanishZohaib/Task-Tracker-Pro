import streamlit as st
import database
import otp_service
from datetime import datetime, timedelta

# Enforce role-based access control (must be logged in and role must be admin)
if "current_user" not in st.session_state or st.session_state.current_user is None:
    st.error("Access Denied: Please log in.")
    st.stop()

# Parse current user name
user_str = st.session_state.current_user
if " (ID: " in user_str:
    user_name, _ = user_str.split(" (ID: ")
else:
    user_name = user_str

current_user_obj = database.get_user_by_name(user_name)
if not current_user_obj or current_user_obj.role != "admin":
    st.error("⛔ Access Denied: You do not have permission to view this page.")
    st.stop()

# Add page title
st.markdown("<h1 style='color: #4F46E5;'>🛠️ Admin Control Panel</h1>", unsafe_allow_html=True)
st.markdown("`Configure settings, manage user accounts, and provide security code assistance.`")
st.markdown("---")

# 1. Overview Statistics
all_users = database.get_users()
total_count = len(all_users)
active_count = sum(1 for u in all_users if u.is_active)
verified_count = sum(1 for u in all_users if u.is_verified)
admin_count = sum(1 for u in all_users if u.role == "admin")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.metric("Total Users", total_count)
with col_stat2:
    st.metric("Active Profiles", active_count, f"{active_count/total_count*100:.0f}% of total" if total_count else None)
with col_stat3:
    st.metric("Verified Profiles", verified_count, f"{verified_count/total_count*100:.0f}% of total" if total_count else None)
with col_stat4:
    st.metric("Administrators", admin_count)

st.markdown("<br>", unsafe_allow_html=True)

# 2. Tabs for different control areas
tab_users, tab_otp = st.tabs(["👤 User Account Management", "📲 OTP Verification Support"])

with tab_users:
    st.markdown("### User Profiles Management")
    st.markdown("Search, view, change roles, activate/deactivate accounts, and manually override passwords.")
    
    # Search
    search_q = st.text_input("🔍 Search user by Username or Mobile Number", key="user_search_q").strip().lower()
    
    # Filter users based on query
    filtered_users = []
    for u in all_users:
        username_match = search_q in u.user_name.lower()
        mobile_match = u.mobile_number and search_q in u.mobile_number.lower()
        fullname_match = u.full_name and search_q in u.full_name.lower()
        if not search_q or username_match or mobile_match or fullname_match:
            filtered_users.append(u)
            
    if not filtered_users:
        st.info("No matching user accounts found.")
    else:
        # Loop through users and show them in styled cards / interactive panels
        for idx, u in enumerate(filtered_users):
            status_color = "#10B981" if u.is_active else "#EF4444"
            status_text = "Active" if u.is_active else "Deactivated"
            verified_badge = "✅ Verified" if u.is_verified else "⏳ Pending verification"
            
            with st.container():
                st.markdown(
                    f"""
                    <div style='background: rgba(248, 250, 252, 0.7); padding: 18px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 12px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='font-size: 1.15rem; font-weight: bold; color: #1E293B;'>{u.full_name or "Legacy User"}</span> 
                                <span style='color: #64748B; font-size: 0.9rem;'>@{u.user_name}</span>
                            </div>
                            <div style='display: flex; gap: 8px;'>
                                <span style='background: {status_color}20; color: {status_color}; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;'>{status_text}</span>
                                <span style='background: #3B82F620; color: #3B82F6; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;'>{u.role.upper()}</span>
                                <span style='background: #E2E8F0; color: #475569; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 500;'>{verified_badge}</span>
                            </div>
                        </div>
                        <div style='color: #64748B; font-size: 0.9rem; margin-top: 5px;'>
                            📱 Mobile: {u.mobile_number or "N/A"} | 📅 Registered: {u.created_date.strftime('%Y-%m-%d %H:%M') if u.created_date else "N/A"}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Interactive Columns for actions
                col_act1, col_act2, col_act3 = st.columns(3)
                
                with col_act1:
                    # Account Status Toggle
                    toggle_label = "Deactivate Profile" if u.is_active else "Activate Profile"
                    # Prevent admin from deactivating themselves
                    disable_status = (u.user_name == user_name)
                    if st.button(toggle_label, key=f"status_btn_{u.user_id}", use_container_width=True, disabled=disable_status):
                        new_status = not u.is_active
                        database.update_user_status(u.user_name, new_status)
                        st.success(f"Updated status for '{u.user_name}' to {'Active' if new_status else 'Inactive'}!")
                        st.rerun()
                        
                with col_act2:
                    # Role Toggle
                    new_role = "user" if u.role == "admin" else "admin"
                    toggle_role_label = "Demote to User" if u.role == "admin" else "Promote to Admin"
                    disable_role = (u.user_name == user_name)
                    if st.button(toggle_role_label, key=f"role_btn_{u.user_id}", use_container_width=True, disabled=disable_role):
                        database.update_user_role(u.user_name, new_role)
                        st.success(f"Changed role of '{u.user_name}' to {new_role}!")
                        st.rerun()
                        
                with col_act3:
                    # Password Reset override expander
                    with st.popover("🔑 Manual Password Reset", use_container_width=True):
                        st.markdown(f"**Override password for {u.user_name}:**")
                        new_pwd = st.text_input("New Password", type="password", key=f"reset_pwd_{u.user_id}")
                        if st.button("Confirm Password Override", key=f"reset_pwd_btn_{u.user_id}", use_container_width=True):
                            if len(new_pwd) >= 4:
                                database.admin_reset_password(u.user_name, new_pwd)
                                st.success("Password updated successfully!")
                            else:
                                st.error("Password must be at least 4 characters.")

with tab_otp:
    st.markdown("### Manual OTP Assistance Desk")
    st.markdown("Generate secure 6-digit codes for users who fail to receive SMS OTPs.")
    
    col_otp_l, col_otp_r = st.columns([1, 1])
    
    with col_otp_l:
        st.markdown("##### 1. Select User Profile")
        otp_users = [u for u in all_users if u.user_name != user_name] # don't reset own password/OTP
        if not otp_users:
            st.info("No other user profiles registered.")
        else:
            selected_otp_user_str = st.selectbox(
                "Search User profile for OTP support",
                options=["-- Select Profile --"] + [f"{u.full_name or 'Legacy'} (@{u.user_name}) - {u.mobile_number or 'No Mobile'}" for u in otp_users]
            )
            
            if selected_otp_user_str != "-- Select Profile --":
                # Extract username
                username_part = selected_otp_user_str.split(" (@")[1].split(")")[0]
                target_user = database.get_user_by_name(username_part)
                
                if target_user:
                    st.markdown(
                        f"""
                        <div style='background: rgba(79, 70, 229, 0.03); padding: 15px; border-radius: 8px; border: 1px solid rgba(79, 70, 229, 0.1); margin-top: 10px;'>
                            <b>User Name</b>: {target_user.full_name or "N/A"}<br>
                            <b>Username/Email</b>: {target_user.user_name}<br>
                            <b>Mobile number</b>: {target_user.mobile_number or "N/A"}<br>
                            <b>Verified</b>: {"Yes" if target_user.is_verified else "No"}<br>
                            <b>Status</b>: {"Active" if target_user.is_active else "Inactive"}<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if not target_user.mobile_number:
                        st.warning("⚠️ This user has no registered mobile number. Manual OTP generation requires a mobile number to ensure link integrity.")
                    else:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("⚡ Generate Assistance OTP", key="admin_gen_otp_btn", use_container_width=True):
                            # Generate OTP
                            new_otp = otp_service.generate_otp()
                            expiry = datetime.utcnow() + timedelta(minutes=10)
                            database.update_user_otp(target_user.user_name, new_otp, expiry)
                            st.session_state.admin_helper_otp_code = new_otp
                            st.session_state.admin_helper_otp_user = target_user.user_name
                            st.success("Successfully generated assistance OTP!")
                            st.rerun()

    with col_otp_r:
        st.markdown("##### 2. Generated Code details")
        if "admin_helper_otp_code" in st.session_state and st.session_state.admin_helper_otp_code:
            target_user = database.get_user_by_name(st.session_state.admin_helper_otp_user)
            if target_user and target_user.otp_code == st.session_state.admin_helper_otp_code:
                st.markdown(
                    f"""
                    <div style='text-align: center; background: rgba(16, 185, 129, 0.05); padding: 25px; border-radius: 12px; border: 2px dashed #10B981;'>
                        <span style='color: #6B7280; font-size: 0.95rem; font-weight: 500;'>SECURE ASSISTANCE CODE FOR @{target_user.user_name}</span>
                        <h1 style='color: #10B981; font-size: 3rem; margin: 10px 0; letter-spacing: 5px;'>{st.session_state.admin_helper_otp_code}</h1>
                        <span style='color: #EF4444; font-size: 0.85rem; font-weight: 600;'>🚨 EXPIRES IN 10 MINUTES (Single-Use Only)</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                col_otp_opt1, col_otp_opt2 = st.columns(2)
                
                with col_otp_opt1:
                    if st.button("📤 Send via SMS", key="send_ass_sms_btn", use_container_width=True):
                        otp_service.send_otp(target_user.mobile_number, st.session_state.admin_helper_otp_code)
                        st.success("Mock SMS triggered!")
                        
                with col_otp_opt2:
                    if st.button("❌ Dismiss Code", key="clear_ass_otp_btn", use_container_width=True):
                        st.session_state.admin_helper_otp_code = None
                        st.session_state.admin_helper_otp_user = None
                        st.rerun()
                        
                st.info(
                    "📢 **Assistance fallback directions:**\n"
                    "- Read the secure 6-digit code verbally to the user.\n"
                    "- Or request them to input it in the verification screen directly.\n"
                    "- Once input, this code will automatically self-destruct from database records."
                )
            else:
                # OTP was cleared from DB (e.g. used by user or expired)
                st.session_state.admin_helper_otp_code = None
                st.session_state.admin_helper_otp_user = None
                st.info("No active assistance codes currently generated or code has expired/been verified.")
        else:
            st.info("Select a user on the left and click 'Generate Assistance OTP' to assist them.")
