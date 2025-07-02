import os
import sqlite3
from dataclasses import dataclass

# Database schema setup
DATABASE_PATH = 'restaurant_analytics.db'

@dataclass
class UploadedFile:
    id: int
    name: str
    file_size: int
    data_type: str
    upload_time: str

@dataclass
class Insight:
    id: int
    file_id: int
    insight_category: str
    insight_details: str
    confidence: float

def create_database():
    """Create SQLite3 database tables if not existing"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            data_type TEXT NOT NULL,
            upload_time TEXT DEFAULT (DATETIME('now'))
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            insight_category TEXT NOT NULL,
            insight_details TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            FOREIGN KEY(file_id) REFERENCES uploaded_files(id)
        )
    """)
    conn.close()

def add_uploaded_file(name: str, file_size: int, data_type: str) -> int:
    """Add new uploaded file record and return its ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO uploaded_files (name, file_size, data_type)
        VALUES (?,?,?) RETURNING id
    """, (name, file_size, data_type))
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return new_id

def log_insight(file_id: int, insight_category: str, insight_details: str, confidence: float=0.8):
    """Store new AI-generated insight"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO insights (file_id, insight_category, insight_details, confidence)
        VALUES (?,?,?,?)
    """, (file_id, insight_category, insight_details, confidence))
    conn.commit()
    conn.close()

def log_error(file_id: int, error_message: str):
    """Log processing errors"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO insights (file_id, insight_category, insight_details, confidence)
        VALUES (?,'error',?,0.0)
    """, (file_id, error_message))
    conn.commit()
    conn.close()

create_database()
print(f"Database initialized at: {DATABASE_PATH}")
