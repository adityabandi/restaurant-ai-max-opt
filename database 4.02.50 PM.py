import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class RestaurantDB:
    def __init__(self, db_path="restaurant_analytics.db"):
        # Use absolute path in production to avoid Streamlit Cloud issues
        import os
        if not os.path.isabs(db_path):
            # In Streamlit Cloud, use a relative path that works
            self.db_path = db_path
        else:
            self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                auth_type TEXT NOT NULL,  -- 'email' or 'google'
                password_hash TEXT,
                google_id TEXT,
                restaurant_name TEXT,
                restaurant_location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Data uploads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_uploads (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                data_type TEXT NOT NULL,  -- 'sales', 'inventory', 'supplier', 'accounting'
                file_size INTEGER,
                columns_detected TEXT,  -- JSON string
                rows_processed INTEGER,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_status TEXT DEFAULT 'completed',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Processed data table (stores actual data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_data (
                id TEXT PRIMARY KEY,
                upload_id TEXT NOT NULL,
                data_json TEXT NOT NULL,  -- JSON string of processed data
                insights_generated TEXT,  -- JSON string of insights
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (upload_id) REFERENCES data_uploads (id)
            )
        ''')
        
        # User insights tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_insights (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                insight_data TEXT NOT NULL,  -- JSON string
                savings_potential REAL,
                implemented BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Weather data cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_cache (
                id TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                weather_data TEXT NOT NULL,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, email: str, name: str, auth_type: str, password: str = None, google_id: str = None) -> str:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        password_hash = None
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (id, email, name, auth_type, password_hash, google_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, email, name, auth_type, password_hash, google_id))
        
        conn.commit()
        conn.close()
        return user_id
    
    def authenticate_user(self, email: str, password: str = None, google_id: str = None) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if google_id:
            cursor.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
        else:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?', (email, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user[0]))
            conn.commit()
            
            # Convert to dict
            user_dict = {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'auth_type': user[3],
                'restaurant_name': user[6],
                'restaurant_location': user[7]
            }
            conn.close()
            return user_dict
        
        conn.close()
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            user_dict = {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'auth_type': user[3],
                'restaurant_name': user[6],
                'restaurant_location': user[7]
            }
            conn.close()
            return user_dict
        
        conn.close()
        return None
    
    def save_data_upload(self, user_id: str, filename: str, data_type: str, 
                        columns_detected: List[str], rows_processed: int, file_size: int) -> str:
        """Save data upload record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        upload_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO data_uploads (id, user_id, filename, data_type, file_size, 
                                    columns_detected, rows_processed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (upload_id, user_id, filename, data_type, file_size, 
              json.dumps(columns_detected), rows_processed))
        
        conn.commit()
        conn.close()
        return upload_id
    
    def save_processed_data(self, upload_id: str, data_json: str, insights: List[Dict] = None) -> str:
        """Save processed data and insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_id = str(uuid.uuid4())
        insights_json = json.dumps(insights) if insights else None
        
        cursor.execute('''
            INSERT INTO processed_data (id, upload_id, data_json, insights_generated)
            VALUES (?, ?, ?, ?)
        ''', (data_id, upload_id, data_json, insights_json))
        
        conn.commit()
        conn.close()
        return data_id
    
    def get_user_uploads(self, user_id: str) -> List[Dict]:
        """Get all uploads for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT du.*, pd.insights_generated 
            FROM data_uploads du
            LEFT JOIN processed_data pd ON du.id = pd.upload_id
            WHERE du.user_id = ?
            ORDER BY du.upload_date DESC
        ''', (user_id,))
        
        uploads = []
        for row in cursor.fetchall():
            upload = {
                'id': row[0],
                'filename': row[2],
                'data_type': row[3],
                'file_size': row[4],
                'columns_detected': json.loads(row[5]) if row[5] else [],
                'rows_processed': row[6],
                'upload_date': row[7],
                'insights': json.loads(row[9]) if row[9] else []
            }
            uploads.append(upload)
        
        conn.close()
        return uploads
    
    def get_processed_data(self, upload_id: str) -> Optional[Dict]:
        """Get processed data for an upload"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data_json, insights_generated FROM processed_data WHERE upload_id = ?', (upload_id,))
        result = cursor.fetchone()
        
        if result:
            data = {
                'data': json.loads(result[0]),
                'insights': json.loads(result[1]) if result[1] else []
            }
            conn.close()
            return data
        
        conn.close()
        return None
    
    def save_user_insight(self, user_id: str, insight_type: str, insight_data: Dict, savings_potential: float = 0):
        """Save user insight"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        insight_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO user_insights (id, user_id, insight_type, insight_data, savings_potential)
            VALUES (?, ?, ?, ?, ?)
        ''', (insight_id, user_id, insight_type, json.dumps(insight_data), savings_potential))
        
        conn.commit()
        conn.close()
        return insight_id
    
    def get_weather_cache(self, location: str, date: str) -> Optional[Dict]:
        """Get cached weather data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT weather_data FROM weather_cache WHERE location = ? AND date = ?', (location, date))
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return json.loads(result[0])
        
        conn.close()
        return None
    
    def save_weather_cache(self, location: str, date: str, weather_data: Dict):
        """Save weather data to cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cache_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO weather_cache (id, location, date, weather_data)
            VALUES (?, ?, ?, ?)
        ''', (cache_id, location, date, json.dumps(weather_data)))
        
        conn.commit()
        conn.close()
    
    def update_user_restaurant_info(self, user_id: str, restaurant_name: str = None, restaurant_location: str = None):
        """Update user restaurant information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if restaurant_name:
            cursor.execute('UPDATE users SET restaurant_name = ? WHERE id = ?', (restaurant_name, user_id))
        
        if restaurant_location:
            cursor.execute('UPDATE users SET restaurant_location = ? WHERE id = ?', (restaurant_location, user_id))
        
        conn.commit()
        conn.close()