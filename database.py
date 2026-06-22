import os
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, desc
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Setup database: dynamic support for Neon (PostgreSQL) and SQLite fallback
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    try:
        import streamlit as st
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except Exception:
        pass

if DATABASE_URL:
    # Clean up the string to remove any accidentally pasted quotes or variable prefixes
    DATABASE_URL = DATABASE_URL.strip().strip("'").strip('"')
    if DATABASE_URL.startswith("DATABASE_URL="):
        DATABASE_URL = DATABASE_URL.replace("DATABASE_URL=", "", 1).strip().strip("'").strip('"')
else:
    DATABASE_URL = "sqlite:///tasktracker.db"

# SQLAlchemy 2.0 requires postgresql:// instead of postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Only apply check_same_thread if SQLite database is used
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String, nullable=True)
    mobile_number = Column(String, unique=True, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Integer, primary_key=True, index=True)
    task_title = Column(String, nullable=False)
    task_description = Column(Text, nullable=True)
    status = Column(String, default="Pending")  # 'Pending' or 'Completed'
    created_by = Column(String, nullable=False)
    created_datetime = Column(DateTime, default=datetime.utcnow)
    edited_by = Column(String, nullable=True)
    edited_datetime = Column(DateTime, nullable=True)
    completed_by = Column(String, nullable=True)
    completed_datetime = Column(DateTime, nullable=True)
    priority = Column(String, default="Normal")  # Dynamically calculated or cached
    is_edited_flag = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, nullable=False)  # 'CREATE', 'EDIT', 'COMPLETE'
    task_id = Column(Integer, nullable=False)
    task_title = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)
    # Dynamic schema migration for existing sqlite/postgresql databases
    from sqlalchemy import inspect, text
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('users')]
        
        with engine.begin() as conn:
            if 'full_name' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))
            if 'mobile_number' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN mobile_number VARCHAR"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_mobile ON users (mobile_number)"))
            if 'is_verified' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
            if 'otp_code' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN otp_code VARCHAR"))
            if 'otp_expiry' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN otp_expiry TIMESTAMP"))
            if 'role' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'"))
            if 'is_active' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
            
            # Data migration: Set existing users (who have NULL mobile number) to verified
            conn.execute(text("UPDATE users SET is_verified = 1 WHERE mobile_number IS NULL"))
            conn.execute(text("UPDATE users SET role = 'user' WHERE role IS NULL"))
            conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
            
        # Seed default admin user if not exists
        admin_user = db.query(User).filter(User.user_name == "admin").first()
        if not admin_user:
            admin_user = User(
                user_name="admin",
                password=hash_password("adminpassword"),
                full_name="Administrator",
                mobile_number="+15550199",
                role="admin",
                is_verified=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Seeded default admin user.")
    except Exception as e:
        print(f"Migration / Seeding detail: {e}")
    finally:
        db.close()

# Helper function to get DB session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# User CRUD Operations
def get_users():
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()

def get_user_by_name(username: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.user_name == username).first()
    finally:
        db.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str, full_name: str = None, mobile_number: str = None):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.user_name == username).first()
        if existing:
            return existing
        
        # Ensure mobile number uniqueness at application level
        if mobile_number:
            existing_mobile = db.query(User).filter(User.mobile_number == mobile_number).first()
            if existing_mobile:
                raise ValueError("Mobile number already registered by another user.")
                
        user = User(
            user_name=username, 
            password=hash_password(password),
            full_name=full_name,
            mobile_number=mobile_number,
            is_verified=False if mobile_number else True,  # auto-verify if no mobile number is specified (for tests/legacy support)
            role="user",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def get_user_by_mobile(mobile_number: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.mobile_number == mobile_number).first()
    finally:
        db.close()

def update_user_otp(username: str, otp_code: str, otp_expiry: datetime):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if user:
            user.otp_code = otp_code
            user.otp_expiry = otp_expiry
            db.commit()
            db.refresh(user)
            return user
        return None
    finally:
        db.close()

def verify_user_otp(username: str, otp_code: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if not user or not user.otp_code or not user.otp_expiry:
            return False
        
        # Expiry check
        if datetime.utcnow() > user.otp_expiry:
            return False
            
        if user.otp_code == otp_code:
            user.is_verified = True
            # Prevent OTP reuse
            user.otp_code = None
            user.otp_expiry = None
            db.commit()
            return True
        return False
    finally:
        db.close()

def update_user_password(username: str, password_raw: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if user:
            user.password = hash_password(password_raw)
            user.is_verified = True  # Verified because they completed reset flow
            user.otp_code = None
            user.otp_expiry = None
            db.commit()
            return True
        return False
    finally:
        db.close()

def update_user_status(username: str, is_active: bool) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if user:
            user.is_active = is_active
            db.commit()
            return True
        return False
    finally:
        db.close()

def update_user_role(username: str, role: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if user:
            user.role = role
            db.commit()
            return True
        return False
    finally:
        db.close()

def admin_reset_password(username: str, new_password_raw: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if user:
            user.password = hash_password(new_password_raw)
            user.is_active = True
            db.commit()
            return True
        return False
    finally:
        db.close()

def verify_user(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
        if not user:
            return False
        return user.password == hash_password(password)
    finally:
        db.close()

# Task CRUD Operations
def create_task(title: str, description: str, created_by: str):
    db = SessionLocal()
    try:
        # Determine initial priority (Normal)
        task = Task(
            task_title=title,
            task_description=description,
            created_by=created_by,
            created_datetime=datetime.now(),
            status="Pending",
            priority="Normal",
            is_edited_flag=False
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Write to audit log
        log = AuditLog(
            action_type="CREATE",
            task_id=task.task_id,
            task_title=task.task_title,
            user_name=created_by,
            timestamp=datetime.now(),
            details=f"Task '{title}' created."
        )
        db.add(log)
        db.commit()
        return task
    finally:
        db.close()

def get_tasks():
    db = SessionLocal()
    try:
        return db.query(Task).all()
    finally:
        db.close()

def get_task(task_id: int):
    db = SessionLocal()
    try:
        return db.query(Task).filter(Task.task_id == task_id).first()
    finally:
        db.close()

def edit_task(task_id: int, title: str, description: str, edited_by: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            return None
        if task.status == "Completed":
            # Locked!
            return None
        
        old_title = task.task_title
        old_desc = task.task_description
        
        task.task_title = title
        task.task_description = description
        task.edited_by = edited_by
        task.edited_datetime = datetime.now()
        task.is_edited_flag = True
        
        # Log audit details
        changes = []
        if old_title != title:
            changes.append(f"Title changed from '{old_title}' to '{title}'")
        if old_desc != description:
            changes.append(f"Description changed")
            
        details = f"Edited by {edited_by}. Changes: " + ", ".join(changes) if changes else f"Edited by {edited_by} with no field changes"
        
        log = AuditLog(
            action_type="EDIT",
            task_id=task.task_id,
            task_title=task.task_title,
            user_name=edited_by,
            timestamp=datetime.now(),
            details=details
        )
        db.add(log)
        db.commit()
        db.refresh(task)
        return task
    finally:
        db.close()

def complete_task(task_id: int, completed_by: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            return None
        if task.status == "Completed":
            return task
        
        task.status = "Completed"
        task.completed_by = completed_by
        task.completed_datetime = datetime.now()
        
        log = AuditLog(
            action_type="COMPLETE",
            task_id=task.task_id,
            task_title=task.task_title,
            user_name=completed_by,
            timestamp=datetime.now(),
            details=f"Task completed by {completed_by}."
        )
        db.add(log)
        db.commit()
        db.refresh(task)
        return task
    finally:
        db.close()

# Audit Logs retrieval
def get_audit_logs():
    db = SessionLocal()
    try:
        return db.query(AuditLog).order_by(desc(AuditLog.timestamp)).all()
    finally:
        db.close()
