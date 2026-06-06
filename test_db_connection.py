"""
Local Database Handshake Verification Script
"""
import sys
import os
from pathlib import Path

# Explicitly declare absolute project paths before any internal imports happen
root_directory = Path(__file__).parent.resolve()
sys.path.insert(0, str(root_directory))
sys.path.insert(0, str(root_directory / 'src'))

from src.db_config import verify_connection, SessionLocal
from sqlalchemy import inspect


print(" Starting Native database handshake checks")


# Check .env
if not os.path.exists(".env"):
    print(" Critical Error: Missing your local .env configuration file!")
    sys.exit(1)

# Check Handshake
if not verify_connection():
    sys.exit(1)

# Inspect Tables
db = SessionLocal()
inspector = inspect(db.get_bind())
cloud_tables = inspector.get_table_names()

print(f"\nScanning remote schemas... Found tables: {cloud_tables}")
db.close()
