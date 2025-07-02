import os
import sqlite3
import json
from typing import List, Dict, Any, Optional

DATABASE_PATH = 'restaurant_analytics.db'

class RestaurantDB:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Table for uploaded files metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                data_type TEXT NOT NULL,
                upload_time TEXT DEFAULT (DATETIME('now'))
            )
        """)

        # Table for insights
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

        # Generic table for storing parsed data (sales, inventory, etc.)
        # Data is stored as JSON string for flexibility
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT UNIQUE NOT NULL,
                data_type TEXT NOT NULL,
                source_file TEXT,
                row_count INTEGER,
                added_at TEXT DEFAULT (DATETIME('now')),
                columns TEXT, -- Stored as JSON string
                data TEXT -- Stored as JSON string
            )
        """)
        
        conn.commit()
        conn.close()

    def add_uploaded_file_metadata(self, name: str, file_size: int, data_type: str) -> int:
        """Add new uploaded file record and return its ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO uploaded_files (name, file_size, data_type)
            VALUES (?,?,?) RETURNING id
        """, (name, file_size, data_type))
        new_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return new_id

    def log_insight(self, file_id: int, insight_category: str, insight_details: str, confidence: float = 0.8):
        """Store new AI-generated insight"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO insights (file_id, insight_category, insight_details, confidence)
            VALUES (?,?,?,?)
        """, (file_id, insight_category, insight_details, confidence))
        conn.commit()
        conn.close()

    def log_error(self, file_id: int, error_message: str):
        """Log processing errors"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO insights (file_id, insight_category, insight_details, confidence)
            VALUES (?,'error',?,0.0)
        """, (file_id, error_message))
        conn.commit()
        conn.close()

    def add_dataset(self, dataset_id: str, data_type: str, data: List[Dict], source_file: str = None) -> bool:
        """Add a new dataset to the 'datasets' table"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            row_count = len(data)
            columns = list(data[0].keys()) if data else []
            cursor.execute("""
                INSERT INTO datasets (dataset_id, data_type, source_file, row_count, columns, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dataset_id, data_type, source_file, row_count, json.dumps(columns), json.dumps(data)))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Dataset with ID {dataset_id} already exists. Updating instead.")
            return self.update_dataset(dataset_id, data_type, data, source_file)
        except Exception as e:
            print(f"Error adding dataset: {e}")
            return False
        finally:
            conn.close()

    def update_dataset(self, dataset_id: str, data_type: str, data: List[Dict], source_file: str = None) -> bool:
        """Update an existing dataset in the 'datasets' table"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            row_count = len(data)
            columns = list(data[0].keys()) if data else []
            cursor.execute("""
                UPDATE datasets
                SET data_type = ?, source_file = ?, row_count = ?, columns = ?, data = ?, added_at = DATETIME('now')
                WHERE dataset_id = ?
            """, (data_type, source_file, row_count, json.dumps(columns), json.dumps(data), dataset_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating dataset: {e}")
            return False
        finally:
            conn.close()

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a dataset by its ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE dataset_id = ?", (dataset_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            # Convert row to dictionary for easier access
            columns = [description[0] for description in cursor.description]
            dataset = dict(zip(columns, row))
            dataset['data'] = json.loads(dataset['data'])
            dataset['columns'] = json.loads(dataset['columns'])
            return dataset
        return None

    def get_all_datasets_metadata(self) -> List[Dict[str, Any]]:
        """Retrieve metadata for all datasets"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT dataset_id, data_type, source_file, row_count, added_at, columns FROM datasets")
        rows = cursor.fetchall()
        conn.close()
        
        datasets_metadata = []
        for row in rows:
            columns = [description[0] for description in cursor.description]
            metadata = dict(zip(columns, row))
            metadata['columns'] = json.loads(metadata['columns'])
            datasets_metadata.append(metadata)
        return datasets_metadata

    def get_datasets_by_type(self, data_type: str) -> List[Dict[str, Any]]:
        """Retrieve all datasets of a specific type"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE data_type = ?", (data_type,))
        rows = cursor.fetchall()
        conn.close()
        
        datasets = []
        for row in rows:
            columns = [description[0] for description in cursor.description]
            dataset = dict(zip(columns, row))
            dataset['data'] = json.loads(dataset['data'])
            dataset['columns'] = json.loads(dataset['columns'])
            datasets.append(dataset)
        return datasets

    def get_all_data_types(self) -> List[str]:
        """Get all unique data types in the warehouse"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT data_type FROM datasets")
        data_types = [row[0] for row in cursor.fetchall()]
        conn.close()
        return data_types

    def get_dataset_count(self) -> int:
        """Get the count of datasets"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM datasets")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_combined_dataset(self, data_type: str) -> List[Dict]:
        """Combine all datasets of a specific type into a single list of dictionaries"""
        datasets = self.get_datasets_by_type(data_type)
        combined_data = []
        for dataset in datasets:
            combined_data.extend(dataset['data'])
        return combined_data

# Initialize the database
db = RestaurantDB()
print(f"Database initialized at: {DATABASE_PATH}")
