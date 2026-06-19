import streamlit as st
import database
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

# Fetch all users
users = database.get_users()
user_list = [u.user_name for u in users]

# Left side branding header (rendered only when logged out)
if st.session_state.current_user is None:
    st.sidebar.markdown(f"# 📋 TaskTracker Pro")
    st.sidebar.markdown("`Track. Monitor. Complete.`")
    st.sidebar.markdown("---")

if st.session_state.current_user is None:
    # Beautiful landing / registration page
    st.markdown("<h1 style='text-align: center; color: #4F46E5;'>📋 TaskTracker Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #6B7280; font-weight: 400;'>Track. Monitor. Complete.</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
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
                if st.button("Enter Workspace", key="enter_ws_btn", use_container_width=True):
                    if database.verify_user(selected_user, login_password):
                        user_obj = database.get_user_by_name(selected_user)
                        st.session_state.current_user = f"{selected_user} (ID: {user_obj.user_id})"
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
        else:
            st.info("No users have been registered yet. Please register on the right to start!")
            
    with col2:
        st.markdown(
            """
            <div style='background: rgba(16, 185, 129, 0.05); padding: 25px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.1);'>
                <h4 style='margin-top:0; color: #10B981;'>📝 Register New Profile</h4>
                <p style='color: #6B7280; font-size: 0.9rem;'>Enter your name to register. This name is mandatory and will be used as the audit signature for task entries.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        new_username = st.text_input("Username / Full Name", placeholder="e.g. Danish Zohaib").strip()
        new_password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register & Enter", key="reg_enter_btn", use_container_width=True):
            if new_username and new_password:
                user_obj = database.create_user(new_username, new_password)
                st.session_state.current_user = f"{new_username} (ID: {user_obj.user_id})"
                st.success(f"Registered profile for '{new_username}'!")
                st.rerun()
            else:
                st.error("Please enter both username and password.")
                
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

    pg = st.navigation({
        "Performance & Stats": [dashboard_page, summary_page],
        "Task Management": [tasks_page, audit_page],
        "Standard Guidelines": [sop_page, manual_page]
    })
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
