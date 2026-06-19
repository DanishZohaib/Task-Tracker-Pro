# TaskTracker Pro
> **Track. Monitor. Complete.**

TaskTracker Application built using Python, Streamlit, and SQLite. Task management application is a modern, professional, and easy-to-use Multi-User Task It helps individuals and teams track, manage, and monitor daily work activities with strict audit logging and compliance rules.

**Application Idea By:** Danish Zohaib

---

## Key Features

- **Payroll KPI Dashboard:** Real-time summary charts (using Plotly) of task status, monthly trends, user performances, and productivity trends.
- **Dynamic Task Aging & Priority:** Tasks are automatically prioritized and color-coded based on their age:
  - 🟢 **Normal**: < 3 days old
  - 🟡 **Medium**: 3 to 7 days old
  - 🔴 **High (Overdue)**: &ge; 7 days old
- **Audit-Compliance Security:** All creations, completions, and edits are permanently captured in an immutable SQL audit log with names and timestamps.
- **Task Lock Rule:** Completed tasks are locked permanently and cannot be modified or deleted.
- **Advanced Filters:** Search tasks and audit logs by title, user name, status, or date range.
- **Comprehensive Reports Export:** Download data in CSV, styled Excel spreadsheets, or summary PDF reports.
- **In-App Guidelines:** Dedicated Standard Operating Procedure (SOP) and interactive User Manual pages.

---

## Technology Stack

- **Framework:** Python 3.12+ & Streamlit
- **Database:** SQLite & SQLAlchemy ORM
- **Libraries:** Pandas, Plotly, OpenPyXL (Excel), ReportLab (PDF)

---

## Local Installation Guide

1. **Clone or Download** this repository to your target directory (e.g. `E:\Antigravity\Todo-app`).
2. **Initialize a Virtual Environment** (Optional but recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   The browser will automatically open to `http://localhost:8501`.

---

## Deployment Instructions

### 1. Streamlit Community Cloud (Recommended)
1. Commit the code and push to a public GitHub repository.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **New app**, select your repository, branch, and entry point (`app.py`).
4. Streamlit Cloud will automatically read `requirements.txt` and launch the app.
5. *Note: SQLite database resets on restart on Streamlit Cloud. For persistent cloud storage, configure a cloud SQL connection or use Git/Persistent disk configurations if available.*

### 2. Windows Server IIS Deployment
1. Install Python 3.12+ on Windows Server.
2. Set up TaskTracker Pro in a directory and install dependencies.
3. Use a service wrapper like **NSSM (Non-Sucking Service Manager)** to run `streamlit run app.py --server.port 80` as a background Windows Service.

### 3. Linux/Docker Deployment
1. Set up a Linux Virtual Machine (Ubuntu/Debian).
2. Install Python, pip, and clone the directory.
3. Run using `nohup` or create a `systemd` unit file:
   ```ini
   [Unit]
   Description=Streamlit TaskTracker Pro App
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Todo-app
   ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port 8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
4. Enable and start the service:
   ```bash
   sudo systemctl enable tasktracker
   sudo systemctl start tasktracker
   ```

---

## Credits
Designed & Conceptualized by **Danish Zohaib**
*Footer credit is displayed on all application views, login pages, and export documents.*
