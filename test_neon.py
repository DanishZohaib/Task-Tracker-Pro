import os
import sys

def test_connection():
    print("--- NEON CONNECTION DIAGNOSTICS ---")
    
    # 1. Check environment variable
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL environment variable is not set in this terminal session.")
        print("Please set it first in CMD (without quotes):")
        print("set DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require")
        return
        
    print(f"Found DATABASE_URL: {db_url[:15]}... [hidden for security] ...{db_url[-15:]}")
    
    # Check for accidental double quotes in CMD
    if db_url.startswith('"') or db_url.endswith('"'):
        print("❌ Error: Your connection URL contains double quotes (\"\").")
        print("In Windows CMD, do NOT use quotes when setting environment variables.")
        print("Fix it by running: set DATABASE_URL=postgresql://...")
        return

    # Check for postgres:// vs postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # 2. Check if psycopg2 is installed
    try:
        import psycopg2
        print("✔ psycopg2-binary driver is installed.")
    except ImportError:
        print("❌ Error: 'psycopg2' library is not installed in your python environment.")
        print("Please run: pip install psycopg2-binary")
        return

    # 3. Try connecting using SQLAlchemy
    try:
        from sqlalchemy import create_engine, text
        print("Connecting to database...")
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            print("✔ CONNECTION SUCCESSFUL!")
            print(f"Postgres Version: {result[0]}")
    except Exception as e:
        print("❌ Error: Failed to connect to the Neon database.")
        print(f"Traceback error details:\n{e}")

if __name__ == "__main__":
    test_connection()
