# Folder Structure Documentation - TaskTracker Pro

The TaskTracker Pro workspace follows a clean, modular folder layout separating database logic, custom user-interface styles, exports, dynamic pages, and deployment documents.

```text
Todo-app/
│
├── app.py                     # Main application entry point & router
├── config.py                  # Configurations (branding credits, aging thresholds, plotly colors)
├── database.py                # Database mappings (SQLAlchemy schemas, ORM logic, CRUD operations)
├── requirements.txt           # Python dependencies installer file
├── README.md                  # Quick-start installation and deployment manuals
│
├── components/                # Reusable UI styles and background helpers
│   ├── custom_styles.py       # Custom CSS injector for gradients, responsive KPI cards, and creator credits
│   └── export_utils.py        # PDF (ReportLab), Excel (OpenPyXL), and CSV exporting scripts
│
├── pages/                     # Individual multi-page scripts run by Streamlit Router
│   ├── dashboard.py           # Payroll Dashboard (Plotly analytics, aging pending list)
│   ├── tasks.py               # Tasks Workspace (Form creations, inline editing, task locking)
│   ├── payroll_tasks_summary.py # Payroll Tasks Summary overview & download control buttons
│   ├── audit_trail.py         # Chronological immutable security logs
│   ├── sop.py                 # Standard Operating Procedure compliance rules page
│   └── user_manual.py         # End-user navigation FAQ booklet
│
└── docs/                      # Comprehensive offline documentation guides
    ├── database_schema.md     # Detailed SQLite schemas and relationships
    ├── folder_structure.md    # [This File]
    ├── sop_documentation.md   # Standard Operating Procedure reference document
    ├── technical_documentation.md # Architecture and logic workflows
    └── user_manual.md         # Full offline copy of the User Reference Manual
```

---

## File Explanations

- **`app.py`**: Initiates SQL connections, loads global CSS styles, coordinates logins, and utilizes Streamlit's routing to navigate between pages in `pages/`.
- **`config.py`**: Simplifies customization by maintaining app metadata, branding variables, aging margins, and Plotly color hex mappings.
- **`database.py`**: Defines standard SQLAlchemy entities mapping to database rows. Provides helper routines for registering profiles, saving tasks, modifying values, logging status, and recording audits.
- **`components/custom_styles.py`**: Injects customized styles for cards, badges, and layout footers.
- **`components/export_utils.py`**: Leverages ReportLab and OpenPyXL to compile binary files for downloads.
- **`pages/`**: Modules loaded dynamically depending on sidebar clicks.
- **`docs/`**: Markdown records detailing structure, operations, guidelines, schemas, and architecture.
