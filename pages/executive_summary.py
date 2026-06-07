import streamlit as st
import pandas as pd
from datetime import datetime
import database
from components.custom_styles import inject_custom_css
from components.export_utils import export_to_csv, export_to_excel, export_to_pdf
from config import AGING_HIGH_THRESHOLD_DAYS, AGING_MEDIUM_THRESHOLD_DAYS, COLORS

inject_custom_css()

st.title("📈 Executive Summary")
st.write("Management-level review and productivity audit reports.")

tasks = database.get_tasks()

# Priority calculations helper
def get_priority_and_age(created_dt, status):
    if not created_dt:
        return "Normal", "🟢", 0
    age_days = (datetime.now() - created_dt).days
    if age_days < 0:
        age_days = 0
    if status == "Completed":
        return "Normal", "🟢", age_days
    
    if age_days >= AGING_HIGH_THRESHOLD_DAYS:
        return "High", "🔴", age_days
    elif age_days >= AGING_MEDIUM_THRESHOLD_DAYS:
        return "Medium", "🟡", age_days
    else:
        return "Normal", "🟢", age_days

if not tasks:
    st.info("No tasks recorded in the system. Use 'Task Manager' to create tasks first.")
else:
    # Compile Dataframe
    data = []
    current_month_str = datetime.now().strftime("%Y-%m")
    
    for t in tasks:
        p_name, p_icon, age_days = get_priority_and_age(t.created_datetime, t.status)
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
    
    total_tasks = len(df)
    pending_tasks = len(df[df["Status"] == "Pending"])
    completed_tasks = len(df[df["Status"] == "Completed"])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    # Task aging counts
    high_aging = len(df[(df["Status"] == "Pending") & (df["Priority"] == "High")])
    med_aging = len(df[(df["Status"] == "Pending") & (df["Priority"] == "Medium")])
    norm_aging = len(df[(df["Status"] == "Pending") & (df["Priority"] == "Normal")])
    
    # 1. Executive Summary KPIs
    st.markdown("<div class='section-header'>Overall Status</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Overall Productivity Score",
            value=f"{completion_rate:.1f}%",
            help="Percentage of tasks completed out of total tasks."
        )
    with col2:
        st.metric(
            label="Total Active Workload",
            value=f"{pending_tasks} Tasks",
            help="Total number of currently pending tasks."
        )
    with col3:
        st.metric(
            label="Completed Work",
            value=f"{completed_tasks} Tasks",
            help="Total number of archived completed tasks."
        )
        
    # 2. Detailed Breakdown Grid
    st.markdown("<div class='section-header'>Operational Breakdowns</div>", unsafe_allow_html=True)
    grid_col1, grid_col2 = st.columns(2)
    
    with grid_col1:
        st.markdown("#### ⏳ Pending Work & Aging Analysis")
        avg_age = df[df["Status"] == "Pending"]["Pending Days"].mean() if pending_tasks > 0 else 0.0
        
        st.markdown(f"- **Total Pending Tasks:** {pending_tasks}")
        st.markdown(f"- **Average Pending Days:** {avg_age:.1f} Days")
        st.markdown(f"- 🔴 **High Priority (Very Old / &ge;7 days):** {high_aging} tasks")
        st.markdown(f"- 🟡 **Medium Priority (Old / &ge;3 days):** {med_aging} tasks")
        st.markdown(f"- 🟢 **Normal Priority (Recent / <3 days):** {norm_aging} tasks")
        
        if high_aging > 0:
            st.warning(f"⚠️ Action Required: There are {high_aging} high priority tasks aging for over {AGING_HIGH_THRESHOLD_DAYS} days!")
            
    with grid_col2:
        st.markdown("#### 👤 Top Active Users")
        # Created counts
        created_counts = df["Created By"].value_counts().reset_index(name="Created")
        created_counts.columns = ["User", "Created Count"]
        
        # Completed counts
        completed_counts = df[df["Status"] == "Completed"]["Completed By"].value_counts().reset_index(name="Completed")
        completed_counts.columns = ["User", "Completed Count"]
        
        user_performance = pd.merge(created_counts, completed_counts, on="User", how="outer").fillna(0)
        user_performance["Created Count"] = user_performance["Created Count"].astype(int)
        user_performance["Completed Count"] = user_performance["Completed Count"].astype(int)
        
        st.dataframe(user_performance.sort_values(by="Completed Count", ascending=False), use_container_width=True, hide_index=True)

    # 3. Monthly Performance Summary Table
    st.markdown("<div class='section-header'>Monthly Performance History</div>", unsafe_allow_html=True)
    
    created_by_month = df.groupby("Created Month").size().reset_index(name="Created")
    completed_by_month = df[df["Status"] == "Completed"].groupby("Completed Month").size().reset_index(name="Completed")
    
    months_list = pd.concat([df["Created Month"], df["Completed Month"]]).dropna().unique()
    months_df = pd.DataFrame({"Month": months_list})
    months_df = months_df[months_df["Month"] != ""].sort_values("Month", ascending=False)
    
    months_df = months_df.merge(created_by_month, left_on="Month", right_on="Created Month", how="left").fillna(0)
    months_df = months_df.merge(completed_by_month, left_on="Month", right_on="Completed Month", how="left").fillna(0)
    months_df = months_df[["Month", "Created", "Completed"]]
    
    # Calculate monthly completion rate
    months_df["Created"] = months_df["Created"].astype(int)
    months_df["Completed"] = months_df["Completed"].astype(int)
    months_df["Monthly Completion %"] = (months_df["Completed"] / months_df["Created"] * 100).apply(lambda x: f"{x:.1f}%" if x < float('inf') and not pd.isna(x) else "0.0%")
    
    st.table(months_df)
    
    # 4. EXPORTS AND DOWNLOADS SECTION
    st.markdown("<div class='section-header'>💼 Export Executive Reports</div>", unsafe_allow_html=True)
    st.write("Download administrative reports summarizing all workspace tasks in PDF, Excel, or CSV format.")
    
    # Prep metrics dict for PDF
    kpis = {
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": high_aging,
        "completion_rate": completion_rate,
        "created_this_month": len(df[df["Created Month"] == current_month_str])
    }
    
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    
    with exp_col1:
        pdf_data = export_to_pdf(df, kpis)
        st.download_button(
            label="📄 Download PDF Summary",
            data=pdf_data,
            file_name=f"tasktracker_executive_summary_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    with exp_col2:
        xlsx_data = export_to_excel(df)
        st.download_button(
            label="📊 Download Excel Spreadsheet",
            data=xlsx_data,
            file_name=f"tasktracker_audit_log_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    with exp_col3:
        csv_data = export_to_csv(df)
        st.download_button(
            label="📝 Download CSV Audit Log",
            data=csv_data,
            file_name=f"tasktracker_audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
