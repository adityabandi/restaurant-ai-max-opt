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
        
        # Enhanced tables for intelligent analytics
        
        # Menu items master table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT,
                base_cost REAL,
                target_price REAL,
                prep_time_minutes INTEGER,
                complexity_score INTEGER,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Individual sales transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                menu_item_id TEXT,
                item_name TEXT NOT NULL,
                transaction_date DATE,
                transaction_time TIME,
                quantity INTEGER,
                unit_price REAL,
                total_amount REAL,
                day_of_week INTEGER,
                hour_of_day INTEGER,
                weather_temp_f INTEGER,
                weather_condition TEXT,
                upload_batch_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
            )
        ''')
        
        # Customer behavior patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_behavior_patterns (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence_score REAL,
                identified_date DATE,
                impact_estimate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Menu performance metrics (daily aggregated)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_performance_metrics (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                menu_item_id TEXT,
                item_name TEXT NOT NULL,
                date DATE,
                total_quantity INTEGER,
                total_revenue REAL,
                avg_price REAL,
                profit_margin REAL,
                rank_by_revenue INTEGER,
                rank_by_quantity INTEGER,
                weather_impact_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
            )
        ''')
        
        # Enhanced actionable insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actionable_insights (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                recommendation TEXT,
                savings_potential REAL,
                confidence_score REAL,
                action_items TEXT,
                affected_items TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Trend analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_analysis (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                trend_type TEXT NOT NULL,
                trend_data TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                strength REAL,
                prediction_accuracy REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
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
    
    # Enhanced methods for intelligent analytics
    
    def save_sales_transactions(self, user_id: str, transactions: List[Dict], upload_batch_id: str):
        """Save individual sales transactions for intelligent analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for transaction in transactions:
            transaction_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO sales_transactions 
                (id, user_id, item_name, transaction_date, transaction_time, 
                 quantity, unit_price, total_amount, upload_batch_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_id, user_id, 
                transaction.get('item_name', ''),
                transaction.get('date'),
                transaction.get('time'),
                transaction.get('quantity', 0),
                transaction.get('price', 0),
                transaction.get('total_amount', 0),
                upload_batch_id
            ))
        
        conn.commit()
        conn.close()
        return len(transactions)
    
    def upsert_menu_item(self, user_id: str, item_name: str, category: str = None, 
                        base_cost: float = None, target_price: float = None):
        """Create or update menu item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if item exists
        cursor.execute('SELECT id FROM menu_items WHERE user_id = ? AND item_name = ?', 
                      (user_id, item_name))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute('''
                UPDATE menu_items 
                SET category = COALESCE(?, category),
                    base_cost = COALESCE(?, base_cost),
                    target_price = COALESCE(?, target_price),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (category, base_cost, target_price, existing[0]))
            item_id = existing[0]
        else:
            # Create new
            item_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO menu_items (id, user_id, item_name, category, base_cost, target_price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (item_id, user_id, item_name, category, base_cost, target_price))
        
        conn.commit()
        conn.close()
        return item_id
    
    def save_actionable_insight(self, user_id: str, insight: Dict):
        """Save intelligent insight to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        insight_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO actionable_insights 
            (id, user_id, insight_type, priority, title, description, 
             recommendation, savings_potential, confidence_score, 
             action_items, affected_items)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            insight_id, user_id,
            insight.get('type', 'general'),
            insight.get('priority', 'medium'),
            insight.get('title', ''),
            insight.get('description', ''),
            insight.get('recommendation', ''),
            insight.get('savings_potential', 0),
            insight.get('confidence_score', 0.8),
            json.dumps(insight.get('action_items', [])),
            json.dumps(insight.get('affected_items', []))
        ))
        
        conn.commit()
        conn.close()
        return insight_id
    
    def get_menu_performance_data(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get menu performance data for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT item_name, 
                   SUM(quantity) as total_quantity,
                   SUM(total_amount) as total_revenue,
                   AVG(unit_price) as avg_price,
                   COUNT(DISTINCT transaction_date) as days_sold
            FROM sales_transactions 
            WHERE user_id = ? AND transaction_date >= date('now', '-' || ? || ' days')
            GROUP BY item_name
            ORDER BY total_revenue DESC
        ''', (user_id, days))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'item_name': row[0],
                'total_quantity': row[1],
                'total_revenue': row[2],
                'avg_price': row[3],
                'days_sold': row[4]
            })
        
        conn.close()
        return results
    
    def get_time_based_patterns(self, user_id: str) -> Dict:
        """Analyze time-based sales patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hour of day analysis
        cursor.execute('''
            SELECT hour_of_day, SUM(total_amount) as hourly_revenue
            FROM sales_transactions 
            WHERE user_id = ? AND hour_of_day IS NOT NULL
            GROUP BY hour_of_day
            ORDER BY hour_of_day
        ''', (user_id,))
        
        hourly_data = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Day of week analysis
        cursor.execute('''
            SELECT day_of_week, SUM(total_amount) as daily_revenue
            FROM sales_transactions 
            WHERE user_id = ? AND day_of_week IS NOT NULL
            GROUP BY day_of_week
            ORDER BY day_of_week
        ''', (user_id,))
        
        daily_data = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return {
            'hourly_patterns': hourly_data,
            'daily_patterns': daily_data
        }