import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import database
from config import AGING_HIGH_THRESHOLD_DAYS, AGING_MEDIUM_THRESHOLD_DAYS, COLORS
from components.custom_styles import inject_custom_css

inject_custom_css()

st.title("📊 Payroll Dashboard")
st.write("Real-time summary of tasks progress, priority metrics, and user performance.")

# Fetch tasks
tasks = database.get_tasks()

# Dynamic Priority and Age Calculations
def compute_priority_and_age(created_dt, status):
    if not created_dt:
        return "Normal", "🟢", 0
    # Handle timezone differences if any
    age_days = (datetime.now() - created_dt).days
    if age_days < 0:
        age_days = 0 # Avoid negative age due to clock discrepancies
        
    if status == "Completed":
        return "Normal", "🟢", age_days
    
    if age_days >= AGING_HIGH_THRESHOLD_DAYS:
        return "High", "🔴", age_days
    elif age_days >= AGING_MEDIUM_THRESHOLD_DAYS:
        return "Medium", "🟡", age_days
    else:
        return "Normal", "🟢", age_days

if not tasks:
    st.info("No tasks registered in the workspace. Go to 'Task Manager' to create your first task!")
else:
    # Build dataframe
    data = []
    current_month_str = datetime.now().strftime("%Y-%m")
    
    for t in tasks:
        p_name, p_icon, age_days = compute_priority_and_age(t.created_datetime, t.status)
        data.append({
            "Task ID": t.task_id,
            "Task Title": t.task_title,
            "Task Description": t.task_description or "",
            "Status": t.status,
            "Created By": t.created_by,
            "Created DateTime": t.created_datetime,
            "Created Month": t.created_datetime.strftime("%Y-%m") if t.created_datetime else "",
            "Completed By": t.completed_by or "",
            "Completed DateTime": t.completed_datetime,
            "Completed Month": t.completed_datetime.strftime("%Y-%m") if t.completed_datetime else "",
            "Pending Days": age_days,
            "Priority": p_name,
            "Priority Icon": p_icon,
            "Is Edited": t.is_edited_flag
        })
    df = pd.DataFrame(data)
    
    # Calculate KPIs
    total_tasks = len(df)
    pending_tasks = len(df[df["Status"] == "Pending"])
    completed_tasks = len(df[df["Status"] == "Completed"])
    
    # Overdue tasks: Pending tasks older than High threshold (7 days)
    overdue_tasks = len(df[(df["Status"] == "Pending") & (df["Pending Days"] >= AGING_HIGH_THRESHOLD_DAYS)])
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    tasks_created_this_month = len(df[df["Created Month"] == current_month_str])
    tasks_completed_this_month = len(df[(df["Status"] == "Completed") & (df["Completed Month"] == current_month_str)])
    
    # Render KPI Cards in HTML/CSS
    st.markdown(
        f"""
        <div class="kpi-container">
            <div class="kpi-card total">
                <div class="kpi-title">Total Tasks</div>
                <div class="kpi-value">{total_tasks}</div>
                <div class="kpi-desc">All registered tasks</div>
            </div>
            <div class="kpi-card pending">
                <div class="kpi-title">Pending</div>
                <div class="kpi-value">{pending_tasks}</div>
                <div class="kpi-desc">Tasks currently in progress</div>
            </div>
            <div class="kpi-card completed">
                <div class="kpi-title">Completed</div>
                <div class="kpi-value">{completed_tasks}</div>
                <div class="kpi-desc">Completion Rate: {completion_rate:.1f}%</div>
            </div>
            <div class="kpi-card overdue">
                <div class="kpi-title">Overdue (&ge;7d)</div>
                <div class="kpi-value">{overdue_tasks}</div>
                <div class="kpi-desc">Urgent actions required</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Secondary KPI cards row
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.metric("Tasks Created This Month", tasks_created_this_month)
    with col_kpi2:
        st.metric("Tasks Completed This Month", tasks_completed_this_month)
        
    st.markdown("<div class='section-header'>Visual Analytics</div>", unsafe_allow_html=True)
    
    # RENDER CHARTS
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 1: Monthly Task Trend (Created, Completed, Pending)
        # Group created tasks by month
        created_by_month = df.groupby("Created Month").size().reset_index(name="Created")
        
        # Group completed tasks by month
        completed_by_month = df[df["Status"] == "Completed"].groupby("Completed Month").size().reset_index(name="Completed")
        
        # Combine
        months_df = pd.DataFrame({"Month": pd.concat([df["Created Month"], df["Completed Month"]]).dropna().unique()})
        months_df = months_df[months_df["Month"] != ""].sort_values("Month")
        months_df = months_df.merge(created_by_month, left_on="Month", right_on="Created Month", how="left").fillna(0)
        months_df = months_df.merge(completed_by_month, left_on="Month", right_on="Completed Month", how="left").fillna(0)
        
        months_df = months_df[["Month", "Created", "Completed"]]
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=months_df["Month"],
            y=months_df["Created"],
            name="Created",
            marker_color=COLORS["primary"]
        ))
        fig_trend.add_trace(go.Bar(
            x=months_df["Month"],
            y=months_df["Completed"],
            name="Completed",
            marker_color=COLORS["success"]
        ))
        fig_trend.update_layout(
            title="Monthly Task Trend (Created vs Completed)",
            barmode='group',
            xaxis_title="Month",
            yaxis_title="Task Count",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col2:
        # Chart 2: Completion Status Chart (Pie Chart)
        status_counts = df["Status"].value_counts().reset_index()
        fig_status = px.pie(
            status_counts,
            values="count",
            names="Status",
            title="Task Completion Status Distribution",
            color="Status",
            color_discrete_map={"Pending": COLORS["warning"], "Completed": COLORS["success"]}
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        fig_status.update_layout(template="plotly_white")
        st.plotly_chart(fig_status, use_container_width=True)
        
    col3, col4 = st.columns(2)
    
    with col3:
        # Chart 3: User Performance Chart
        # Group tasks created by user
        created_by_user = df.groupby("Created By").size().reset_index(name="Created")
        
        # Group tasks completed by user
        completed_by_user = df[df["Status"] == "Completed"].groupby("Completed By").size().reset_index(name="Completed")
        
        # Combine
        all_users_in_tasks = pd.concat([df["Created By"], df["Completed By"]]).dropna().unique()
        users_df = pd.DataFrame({"User": all_users_in_tasks})
        users_df = users_df[users_df["User"] != ""].sort_values("User")
        
        users_df = users_df.merge(created_by_user, left_on="User", right_on="Created By", how="left").fillna(0)
        users_df = users_df.merge(completed_by_user, left_on="User", right_on="Completed By", how="left").fillna(0)
        users_df = users_df[["User", "Created", "Completed"]]
        
        fig_user = go.Figure()
        fig_user.add_trace(go.Bar(
            y=users_df["User"],
            x=users_df["Created"],
            name="Created",
            orientation='h',
            marker_color=COLORS["info"]
        ))
        fig_user.add_trace(go.Bar(
            y=users_df["User"],
            x=users_df["Completed"],
            name="Completed",
            orientation='h',
            marker_color=COLORS["success"]
        ))
        fig_user.update_layout(
            title="User Performance Metrics",
            barmode='group',
            xaxis_title="Count of Tasks",
            yaxis_title="User Name",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_user, use_container_width=True)
        
    with col4:
        # Chart 4: Productivity Trend (Monthly completion rate)
        # We plot the completion rate by month: (Completed in month / Total created in month) or count of tasks completed.
        # Let's show completed tasks by month as a line trend
        fig_productivity = px.line(
            months_df,
            x="Month",
            y="Completed",
            title="Monthly Productivity Trend (Completed Count)",
            markers=True,
            line_shape="linear"
        )
        fig_productivity.update_traces(line_color=COLORS["secondary"], line_width=3)
        fig_productivity.update_layout(
            xaxis_title="Month",
            yaxis_title="Tasks Completed",
            template="plotly_white"
        )
        st.plotly_chart(fig_productivity, use_container_width=True)
        
    st.markdown("<div class='section-header'>Pending Work Priorities (Sorted by Age - Oldest First)</div>", unsafe_allow_html=True)
    
    # Pending tasks sorted: oldest at top, newest at bottom
    pending_df = df[df["Status"] == "Pending"].copy()
    if pending_df.empty:
        st.success("🎉 Excellent! There are no pending tasks. Enjoy your clean desk!")
    else:
        pending_df = pending_df.sort_values(by="Created DateTime", ascending=True)
        
        # Format dates for table display
        pending_df["Creation Date"] = pending_df["Created DateTime"].apply(lambda x: x.strftime('%Y-%m-%d %H:%M') if x else "")
        pending_df["Pending (Days)"] = pending_df["Pending Days"].apply(lambda x: f"{x}d" if x > 0 else "<1d")
        
        # Rename and select columns
        display_df = pending_df[[
            "Priority Icon", "Task ID", "Task Title", "Task Description", 
            "Created By", "Creation Date", "Pending (Days)"
        ]].rename(columns={
            "Priority Icon": "Priority"
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown(
            """
            <small style='color: #6B7280;'>
                <b>Aging Guide:</b> 🔴 High Priority (&ge;7 days old) | 🟡 Medium Priority (&ge;3 days old) | 🟢 Normal Priority (<3 days old)
            </small>
            """,
            unsafe_allow_html=True
        )
