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

# Left side branding header
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
    # Sidebar user details
    st.sidebar.markdown(f"👤 **Logged in as:**\n**{st.session_state.current_user}**")
    if st.sidebar.button("Logout / Switch User", use_container_width=True, key="logout_btn"):
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Navigation mapping using Streamlit Pages
    dashboard_page = st.Page("pages/dashboard.py", title="Payroll Dashboard", icon="📊", default=True)
    tasks_page = st.Page("pages/tasks.py", title="Task Manager", icon="📝")
    summary_page = st.Page("pages/executive_summary.py", title="Executive Summary", icon="📈")
    audit_page = st.Page("pages/audit_trail.py", title="Audit Trail", icon="🔒")
    sop_page = st.Page("pages/sop.py", title="SOP Compliance", icon="📋")
    manual_page = st.Page("pages/user_manual.py", title="User Manual", icon="📖")

    pg = st.navigation({
        "Performance & Stats": [dashboard_page, summary_page],
        "Task Management": [tasks_page, audit_page],
        "Standard Guidelines": [sop_page, manual_page]
    })
    pg.run()
    
    draw_footer()
