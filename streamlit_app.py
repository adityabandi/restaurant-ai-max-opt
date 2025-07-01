#!/usr/bin/env python3
"""
Restaurant Analytics Pro - Premium Restaurant Data Analytics Platform
A sophisticated yet simple analytics tool for restaurant owners
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json
import os
from typing import Dict, List, Optional, Any

# ============================================================================
# PAGE CONFIGURATION - Must be first Streamlit command
# ============================================================================
st.set_page_config(
    page_title="Restaurant Analytics Pro",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Restaurant Analytics Pro - Turn your data into profits"
    }
)

# ============================================================================
# PREMIUM UI STYLING
# ============================================================================
def load_custom_css():
    """Load premium custom CSS styling"""
    st.markdown("""
    <style>
        /* Import premium fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Root variables for consistent theming */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --text-primary: #1a1a1a;
            --text-secondary: #666666;
            --surface-white: #ffffff;
            --surface-light: #f8fafc;
            --border-light: #e2e8f0;
            --shadow-light: 0 4px 6px rgba(0, 0, 0, 0.05);
            --shadow-medium: 0 10px 25px rgba(0, 0, 0, 0.1);
            --shadow-heavy: 0 20px 40px rgba(0, 0, 0, 0.15);
            --border-radius: 12px;
            --border-radius-large: 20px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Global app styling */
        .stApp {
            background: var(--background-gradient);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text-primary);
        }
        
        /* Hide Streamlit default elements */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
        .stDeployButton { display: none; }
        
        /* Main container with glass morphism effect */
        .main-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            margin: 1.5rem;
            border-radius: var(--border-radius-large);
            padding: 2.5rem;
            box-shadow: var(--shadow-heavy);
            border: 1px solid rgba(255, 255, 255, 0.2);
            min-height: 85vh;
        }
        
        /* Header section */
        .app-header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem 0;
            border-bottom: 2px solid var(--surface-light);
        }
        
        .app-title {
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 800;
            background: var(--background-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
            line-height: 1.2;
        }
        
        .app-subtitle {
            font-size: clamp(1rem, 2vw, 1.3rem);
            color: var(--text-secondary);
            font-weight: 400;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }
        
        /* Premium card styling */
        .premium-card {
            background: var(--surface-white);
            border-radius: var(--border-radius);
            padding: 2rem;
            box-shadow: var(--shadow-light);
            margin-bottom: 2rem;
            border: 1px solid var(--border-light);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }
        
        .premium-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--background-gradient);
            transform: translateX(-100%);
            transition: var(--transition);
        }
        
        .premium-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-medium);
        }
        
        .premium-card:hover::before {
            transform: translateX(0);
        }
        
        .card-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .card-subtitle {
            color: var(--text-secondary);
            font-size: 1rem;
            line-height: 1.5;
            margin-bottom: 1.5rem;
        }
        
        /* Metrics grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .metric-card {
            background: linear-gradient(135deg, var(--surface-light) 0%, #e2e8f0 100%);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            text-align: center;
            border: 1px solid var(--border-light);
            transition: var(--transition);
        }
        
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-light);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
            line-height: 1;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Insight cards */
        .insight-card {
            background: var(--surface-light);
            border-left: 4px solid var(--primary-color);
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 0 var(--border-radius) var(--border-radius) 0;
            transition: var(--transition);
        }
        
        .insight-card:hover {
            background: var(--surface-white);
            transform: translateX(5px);
            box-shadow: var(--shadow-light);
        }
        
        .insight-title {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        
        .insight-text {
            color: var(--text-secondary);
            line-height: 1.6;
            font-size: 0.95rem;
        }
        
        /* Premium buttons */
        .stButton > button {
            background: var(--background-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--border-radius) !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: var(--transition) !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
            text-transform: none !important;
            letter-spacing: 0.3px !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* File uploader styling */
        .stFileUploader > div > div {
            background: var(--surface-light) !important;
            border: 2px dashed var(--border-light) !important;
            border-radius: var(--border-radius) !important;
            padding: 2rem !important;
            text-align: center !important;
            transition: var(--transition) !important;
        }
        
        .stFileUploader > div > div:hover {
            border-color: var(--primary-color) !important;
            background: rgba(102, 126, 234, 0.05) !important;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--surface-light) !important;
            border-radius: var(--border-radius) !important;
            padding: 0.5rem !important;
            margin-bottom: 2rem !important;
            border: 1px solid var(--border-light) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            color: var(--text-secondary) !important;
            transition: var(--transition) !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(102, 126, 234, 0.1) !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--background-gradient) !important;
            color: white !important;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border-radius: var(--border-radius) !important;
            padding: 1rem !important;
            font-weight: 500 !important;
            border: none !important;
        }
        
        .stError {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
            color: white !important;
            border-radius: var(--border-radius) !important;
            padding: 1rem !important;
            font-weight: 500 !important;
            border: none !important;
        }
        
        .stInfo {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            border-radius: var(--border-radius) !important;
            padding: 1rem !important;
            font-weight: 500 !important;
            border: none !important;
        }
        
        /* Loading spinner */
        .stSpinner > div {
            border-top-color: var(--primary-color) !important;
        }
        
        /* DataFrame styling */
        .stDataFrame {
            border-radius: var(--border-radius) !important;
            overflow: hidden !important;
            box-shadow: var(--shadow-light) !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-container {
                margin: 1rem;
                padding: 1.5rem;
            }
            
            .app-title {
                font-size: 2.5rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }
            
            .metric-value {
                font-size: 2rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# CLAUDE AI PLACEHOLDER CLASS
# ============================================================================
class ClaudeAI:
    """
    Placeholder for Claude AI integration - Ready for future activation
    
    To activate:
    1. Add ANTHROPIC_API_KEY to environment
    2. Uncomment the anthropic import and client initialization
    3. Replace placeholder methods with actual API calls
    """
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.available = False
        
        # Uncomment when ready to use Claude API:
        # try:
        #     import anthropic
        #     if self.api_key:
        #         self.client = anthropic.Anthropic(api_key=self.api_key)
        #         self.available = True
        # except ImportError:
        #     pass
    
    def analyze_complex_query(self, data: pd.DataFrame, query: str) -> Dict[str, Any]:
        """
        Placeholder for Claude AI complex analysis
        
        When activated, this will:
        1. Send data summary + query to Claude
        2. Get intelligent business insights
        3. Return formatted analysis
        """
        return {
            'available': self.available,
            'response': 'Advanced AI analysis coming soon! Currently using smart pattern detection.',
            'confidence': 0.0,
            'recommendations': []
        }

# ============================================================================
# DATA PROCESSING UTILITIES
# ============================================================================
class DataProcessor:
    """Robust data processing with comprehensive error handling"""
    
    @staticmethod
    def read_file(uploaded_file) -> tuple[bool, pd.DataFrame, str]:
        """
        Read uploaded file with multiple fallback strategies
        
        Returns:
            tuple: (success: bool, dataframe: pd.DataFrame, message: str)
        """
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Reset file pointer
            uploaded_file.seek(0)
            
            if file_extension == 'csv':
                # Try multiple encodings for CSV
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
                separators = [',', ';', '\t', '|']
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, encoding=encoding, sep=sep)
                            if len(df.columns) > 1 and len(df) > 0:
                                # Clean the dataframe
                                df = DataProcessor._clean_dataframe(df)
                                return True, df, f"✅ CSV loaded successfully (encoding: {encoding})"
                        except Exception:
                            continue
                
                # Last resort: try with error handling
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='utf-8', errors='replace')
                    df = DataProcessor._clean_dataframe(df)
                    return True, df, "✅ CSV loaded with error correction"
                except Exception as e:
                    return False, pd.DataFrame(), f"❌ CSV reading failed: {str(e)}"
            
            elif file_extension in ['xlsx', 'xls']:
                # Try Excel reading with multiple engines
                engines = ['openpyxl', 'xlrd'] if file_extension == 'xls' else ['openpyxl']
                
                for engine in engines:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_excel(uploaded_file, engine=engine)
                        if len(df.columns) > 0 and len(df) > 0:
                            df = DataProcessor._clean_dataframe(df)
                            return True, df, f"✅ Excel loaded successfully (engine: {engine})"
                    except Exception:
                        continue
                
                return False, pd.DataFrame(), "❌ Excel reading failed - file may be corrupted"
            
            else:
                return False, pd.DataFrame(), f"❌ Unsupported file type: .{file_extension}"
        
        except Exception as e:
            return False, pd.DataFrame(), f"❌ File processing error: {str(e)}"
    
    @staticmethod
    def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Clean column names
        df.columns = [str(col).strip().replace('\n', ' ').replace('\r', ' ') for col in df.columns]
        
        # Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    @staticmethod
    def detect_data_type(df: pd.DataFrame, filename: str) -> str:
        """Intelligently detect restaurant data type"""
        columns_lower = [col.lower().strip() for col in df.columns]
        filename_lower = filename.lower()
        
        # Define patterns for different data types
        patterns = {
            'sales': {
                'keywords': ['sales', 'revenue', 'transaction', 'order', 'pos', 'receipt'],
                'columns': ['item', 'product', 'quantity', 'price', 'amount', 'total', 'revenue']
            },
            'inventory': {
                'keywords': ['inventory', 'stock', 'warehouse', 'count'],
                'columns': ['item', 'product', 'stock', 'quantity', 'on hand', 'available']
            },
            'menu': {
                'keywords': ['menu', 'recipe', 'dish'],
                'columns': ['item', 'dish', 'recipe', 'ingredient', 'category']
            }
        }
        
        # Check filename first
        for data_type, config in patterns.items():
            for keyword in config['keywords']:
                if keyword in filename_lower:
                    return data_type
        
        # Check column patterns
        best_match = 'other'
        best_score = 0
        
        for data_type, config in patterns.items():
            score = sum(1 for pattern in config['columns'] 
                       if any(pattern in col for col in columns_lower))
            if score > best_score:
                best_score = score
                best_match = data_type
        
        return best_match if best_score >= 2 else 'other'

# ============================================================================
# INSIGHT GENERATOR
# ============================================================================
class InsightGenerator:
    """Generate actionable business insights from restaurant data"""
    
    @staticmethod
    def generate_insights(df: pd.DataFrame, data_type: str) -> List[Dict[str, Any]]:
        """Generate comprehensive insights based on data type"""
        insights = []
        
        if df.empty:
            return insights
        
        # Standardize column detection
        columns = {col.lower().strip(): col for col in df.columns}
        
        # Sales data insights
        if data_type == 'sales':
            insights.extend(InsightGenerator._generate_sales_insights(df, columns))
        
        # Inventory data insights
        elif data_type == 'inventory':
            insights.extend(InsightGenerator._generate_inventory_insights(df, columns))
        
        # Menu data insights
        elif data_type == 'menu':
            insights.extend(InsightGenerator._generate_menu_insights(df, columns))
        
        # General insights for any data type
        insights.extend(InsightGenerator._generate_general_insights(df, columns))
        
        return insights
    
    @staticmethod
    def _generate_sales_insights(df: pd.DataFrame, columns: dict) -> List[Dict[str, Any]]:
        """Generate sales-specific insights"""
        insights = []
        
        # Find revenue/amount columns
        revenue_cols = [col for key, col in columns.items() 
                       if any(term in key for term in ['revenue', 'total', 'amount', 'sales'])]
        
        # Find item columns
        item_cols = [col for key, col in columns.items() 
                    if any(term in key for term in ['item', 'product', 'dish', 'name'])]
        
        # Find quantity columns
        qty_cols = [col for key, col in columns.items() 
                   if any(term in key for term in ['quantity', 'qty', 'count'])]
        
        if revenue_cols and item_cols:
            revenue_col = revenue_cols[0]
            item_col = item_cols[0]
            
            # Convert to numeric
            df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
            
            # Top revenue generator
            top_revenue_item = df.loc[df[revenue_col].idxmax(), item_col]
            top_revenue_amount = df[revenue_col].max()
            total_revenue = df[revenue_col].sum()
            
            insights.append({
                'icon': '💰',
                'title': f'{top_revenue_item} is your revenue champion',
                'text': f'Generated ${top_revenue_amount:,.2f} ({(top_revenue_amount/total_revenue*100):.1f}% of total revenue). This superstar should be prominently featured on your menu.',
                'type': 'revenue',
                'priority': 'high'
            })
            
            # Low performers
            low_threshold = df[revenue_col].quantile(0.3)
            low_performers = df[df[revenue_col] < low_threshold]
            
            if len(low_performers) > 0:
                insights.append({
                    'icon': '📉',
                    'title': f'{len(low_performers)} items need attention',
                    'text': f'These items are underperforming with revenue below ${low_threshold:.2f}. Consider promotions, recipe improvements, or menu optimization.',
                    'type': 'optimization',
                    'priority': 'medium'
                })
        
        # Quantity insights
        if qty_cols and item_cols:
            qty_col = qty_cols[0]
            item_col = item_cols[0]
            
            df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce')
            
            top_seller = df.loc[df[qty_col].idxmax(), item_col]
            top_quantity = df[qty_col].max()
            
            insights.append({
                'icon': '🔥',
                'title': f'{top_seller} flies off the menu',
                'text': f'With {top_quantity:,.0f} units sold, this is clearly a customer favorite. Consider creating variations or highlighting it in marketing.',
                'type': 'popularity',
                'priority': 'high'
            })
        
        return insights
    
    @staticmethod
    def _generate_inventory_insights(df: pd.DataFrame, columns: dict) -> List[Dict[str, Any]]:
        """Generate inventory-specific insights"""
        insights = []
        
        # Find stock/quantity columns
        stock_cols = [col for key, col in columns.items() 
                     if any(term in key for term in ['stock', 'quantity', 'on hand', 'available'])]
        
        # Find item columns
        item_cols = [col for key, col in columns.items() 
                    if any(term in key for term in ['item', 'product', 'name'])]
        
        if stock_cols and item_cols:
            stock_col = stock_cols[0]
            item_col = item_cols[0]
            
            df[stock_col] = pd.to_numeric(df[stock_col], errors='coerce')
            
            # Low stock alerts
            low_stock_threshold = 10
            low_stock_items = df[df[stock_col] < low_stock_threshold]
            
            if len(low_stock_items) > 0:
                critical_item = low_stock_items.loc[low_stock_items[stock_col].idxmin(), item_col]
                critical_quantity = low_stock_items[stock_col].min()
                
                insights.append({
                    'icon': '⚠️',
                    'title': 'Stock emergency alert!',
                    'text': f'{len(low_stock_items)} items are critically low. {critical_item} has only {critical_quantity:.0f} units left. Order immediately to avoid stockouts.',
                    'type': 'critical',
                    'priority': 'high'
                })
            
            # Overstock analysis
            high_stock_threshold = df[stock_col].quantile(0.9)
            overstock_items = df[df[stock_col] > high_stock_threshold]
            
            if len(overstock_items) > 0:
                insights.append({
                    'icon': '📦',
                    'title': f'{len(overstock_items)} items are overstocked',
                    'text': f'Consider running promotions on these items to free up storage space and improve cash flow.',
                    'type': 'optimization',
                    'priority': 'medium'
                })
        
        return insights
    
    @staticmethod
    def _generate_menu_insights(df: pd.DataFrame, columns: dict) -> List[Dict[str, Any]]:
        """Generate menu-specific insights"""
        insights = []
        
        # Category analysis
        category_cols = [col for key, col in columns.items() 
                        if any(term in key for term in ['category', 'type', 'class'])]
        
        if category_cols:
            category_col = category_cols[0]
            category_counts = df[category_col].value_counts()
            
            if len(category_counts) > 0:
                top_category = category_counts.index[0]
                top_count = category_counts.iloc[0]
                
                insights.append({
                    'icon': '🏆',
                    'title': f'{top_category} dominates your menu',
                    'text': f'With {top_count} items, this category has the most variety. Ensure it aligns with customer demand and profitability.',
                    'type': 'menu_structure',
                    'priority': 'medium'
                })
        
        return insights
    
    @staticmethod
    def _generate_general_insights(df: pd.DataFrame, columns: dict) -> List[Dict[str, Any]]:
        """Generate general data insights"""
        insights = []
        
        # Data quality insight
        total_rows = len(df)
        total_columns = len(df.columns)
        missing_data_pct = (df.isnull().sum().sum() / (total_rows * total_columns)) * 100
        
        if missing_data_pct > 20:
            insights.append({
                'icon': '🔍',
                'title': 'Data quality needs attention',
                'text': f'{missing_data_pct:.1f}% of your data is missing. Consider improving data collection processes for better insights.',
                'type': 'data_quality',
                'priority': 'low'
            })
        elif missing_data_pct < 5:
            insights.append({
                'icon': '✅',
                'title': 'Excellent data quality',
                'text': f'Only {missing_data_pct:.1f}% missing data. Your data collection is top-notch, enabling accurate analysis.',
                'type': 'data_quality',
                'priority': 'low'
            })
        
        return insights

# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================
class RestaurantAnalyticsPro:
    """Premium Restaurant Analytics Application"""
    
    def __init__(self):
        """Initialize the application"""
        self.claude_ai = ClaudeAI()
        self.data_processor = DataProcessor()
        self.insight_generator = InsightGenerator()
        
        # Initialize session state
        if 'app_data' not in st.session_state:
            st.session_state.app_data = None
        if 'insights' not in st.session_state:
            st.session_state.insights = []
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 'upload'
    
    def run(self):
        """Main application entry point"""
        # Load custom CSS
        load_custom_css()
        
        # Main container
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Header
        self._render_header()
        
        # Main content based on current view
        if st.session_state.current_view == 'upload':
            self._render_upload_page()
        elif st.session_state.current_view == 'dashboard':
            self._render_dashboard()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_header(self):
        """Render the application header"""
        st.markdown("""
        <div class="app-header">
            <div class="app-title">🍽️ Restaurant Analytics Pro</div>
            <div class="app-subtitle">
                Transform your restaurant data into actionable insights and boost your profits with AI-powered analytics
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_upload_page(self):
        """Render the file upload page"""
        # Center the upload interface
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Upload card
            st.markdown("""
            <div class="premium-card">
                <div class="card-title">📊 Upload Your Restaurant Data</div>
                <div class="card-subtitle">
                    Upload your sales data, inventory reports, or any restaurant CSV/Excel files to get instant, actionable insights that can boost your profits.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose your data file",
                type=['csv', 'xlsx', 'xls'],
                help="Supported formats: CSV, Excel (.xlsx, .xls)",
                key="main_uploader"
            )
            
            if uploaded_file is not None:
                self._process_uploaded_file(uploaded_file)
            
            # Divider
            st.markdown("---")
            
            # Demo data section
            st.markdown("""
            <div class="premium-card">
                <div class="card-title">🚀 Try Demo Data</div>
                <div class="card-subtitle">
                    See the platform in action with realistic restaurant data and discover insights that could save you thousands monthly.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎯 LOAD DEMO RESTAURANT DATA", key="demo_button", use_container_width=True):
                self._load_demo_data()
    
    def _process_uploaded_file(self, uploaded_file):
        """Process the uploaded file"""
        with st.spinner("🔍 Analyzing your data..."):
            # Read the file
            success, df, message = self.data_processor.read_file(uploaded_file)
            
            if success:
                # Detect data type
                data_type = self.data_processor.detect_data_type(df, uploaded_file.name)
                
                # Store data
                st.session_state.app_data = {
                    'filename': uploaded_file.name,
                    'dataframe': df,
                    'data_type': data_type,
                    'rows': len(df),
                    'columns': list(df.columns),
                    'upload_time': datetime.now()
                }
                
                # Generate insights
                insights = self.insight_generator.generate_insights(df, data_type)
                st.session_state.insights = insights
                
                # Switch to dashboard
                st.session_state.current_view = 'dashboard'
                
                st.success(f"{message} - {len(df)} rows processed")
                st.rerun()
            
            else:
                st.error(message)
                st.info("💡 **Tip**: Ensure your file has proper headers and contains restaurant data like sales, inventory, or menu information.")
    
    def _load_demo_data(self):
        """Load demonstration data"""
        # Create realistic demo data
        demo_data = pd.DataFrame({
            'Item': [
                'Classic Burger', 'Caesar Salad', 'Margherita Pizza', 'Grilled Salmon',
                'Chicken Wings', 'Fish Tacos', 'Craft Beer', 'House Wine',
                'Chocolate Cake', 'Truffle Pasta', 'BBQ Ribs', 'Vegetable Curry'
            ],
            'Category': [
                'Entrees', 'Salads', 'Pizza', 'Entrees',
                'Appetizers', 'Entrees', 'Beverages', 'Beverages',
                'Desserts', 'Pasta', 'Entrees', 'Entrees'
            ],
            'Quantity': [45, 12, 28, 22, 35, 19, 67, 31, 15, 8, 18, 9],
            'Unit_Price': [16.99, 14.99, 18.99, 24.99, 12.99, 15.99, 6.99, 8.99, 7.99, 26.99, 22.99, 16.99],
            'Total_Revenue': [764.55, 179.88, 531.72, 549.78, 454.65, 303.81, 468.33, 278.69, 119.85, 215.92, 413.82, 152.91]
        })
        
        # Store demo data
        st.session_state.app_data = {
            'filename': '🎯 Demo Restaurant Data',
            'dataframe': demo_data,
            'data_type': 'sales',
            'rows': len(demo_data),
            'columns': list(demo_data.columns),
            'upload_time': datetime.now()
        }
        
        # Generate insights
        insights = self.insight_generator.generate_insights(demo_data, 'sales')
        st.session_state.insights = insights
        
        # Switch to dashboard
        st.session_state.current_view = 'dashboard'
        
        st.success("🎉 Demo data loaded! Explore your restaurant insights below.")
        st.rerun()
    
    def _render_dashboard(self):
        """Render the main dashboard"""
        data = st.session_state.app_data
        df = data['dataframe']
        
        # Dashboard header with file info
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="premium-card">
                <div class="card-title">📄 {data['filename']}</div>
                <div class="card-subtitle">
                    Analyzing {data['rows']:,} rows of {data['data_type']} data • 
                    {len(data['columns'])} columns • 
                    Uploaded {data['upload_time'].strftime('%B %d, %Y at %I:%M %p')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("⬆️ Upload New File", key="new_upload_button"):
                st.session_state.current_view = 'upload'
                st.session_state.app_data = None
                st.session_state.insights = []
                st.rerun()
        
        # Key metrics (if we have revenue/quantity data)
        self._render_key_metrics(df)
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs([
            "💡 Smart Insights", 
            "📊 Data Analysis", 
            "🤖 AI Assistant"
        ])
        
        with tab1:
            self._render_insights_tab()
        
        with tab2:
            self._render_analysis_tab(df)
        
        with tab3:
            self._render_ai_tab(df)
    
    def _render_key_metrics(self, df: pd.DataFrame):
        """Render key metrics cards"""
        # Try to find relevant columns
        columns = {col.lower().strip(): col for col in df.columns}
        
        # Find revenue columns
        revenue_cols = [col for key, col in columns.items() 
                       if any(term in key for term in ['revenue', 'total', 'amount', 'sales'])]
        
        # Find quantity columns
        qty_cols = [col for key, col in columns.items() 
                   if any(term in key for term in ['quantity', 'qty', 'count'])]
        
        if revenue_cols or qty_cols:
            metrics_html = '<div class="metrics-grid">'
            
            # Total items metric
            metrics_html += f'''
            <div class="metric-card">
                <div class="metric-value">{len(df):,}</div>
                <div class="metric-label">Total Items</div>
            </div>
            '''
            
            # Revenue metrics
            if revenue_cols:
                revenue_col = revenue_cols[0]
                df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
                total_revenue = df[revenue_col].sum()
                avg_revenue = df[revenue_col].mean()
                
                metrics_html += f'''
                <div class="metric-card">
                    <div class="metric-value">${total_revenue:,.0f}</div>
                    <div class="metric-label">Total Revenue</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${avg_revenue:.2f}</div>
                    <div class="metric-label">Avg Revenue</div>
                </div>
                '''
            
            # Quantity metrics
            if qty_cols:
                qty_col = qty_cols[0]
                df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce')
                total_qty = df[qty_col].sum()
                
                metrics_html += f'''
                <div class="metric-card">
                    <div class="metric-value">{total_qty:,.0f}</div>
                    <div class="metric-label">Units Sold</div>
                </div>
                '''
            
            metrics_html += '</div>'
            st.markdown(metrics_html, unsafe_allow_html=True)
    
    def _render_insights_tab(self):
        """Render the insights tab"""
        insights = st.session_state.insights
        
        if insights:
            st.markdown("""
            <div class="premium-card">
                <div class="card-title">🧠 AI-Generated Insights</div>
                <div class="card-subtitle">
                    Our advanced analytics have identified key opportunities to boost your restaurant's performance.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Sort insights by priority
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_insights = sorted(insights, key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))
            
            for insight in sorted_insights:
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">{insight.get('icon', '💡')} {insight.get('title', 'Insight')}</div>
                    <div class="insight-text">{insight.get('text', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🔍 No insights generated yet. This might happen if your data structure is unique. Try the AI Assistant tab for custom analysis!")
    
    def _render_analysis_tab(self, df: pd.DataFrame):
        """Render the data analysis tab"""
        # Data preview
        st.markdown("""
        <div class="premium-card">
            <div class="card-title">📋 Data Preview</div>
            <div class="card-subtitle">First 10 rows of your uploaded data</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(df.head(10), use_container_width=True)
        
        # Charts section
        self._render_charts(df)
    
    def _render_charts(self, df: pd.DataFrame):
        """Render data visualization charts"""
        columns = {col.lower().strip(): col for col in df.columns}
        
        # Find relevant columns
        item_cols = [col for key, col in columns.items() 
                    if any(term in key for term in ['item', 'product', 'dish', 'name'])]
        revenue_cols = [col for key, col in columns.items() 
                       if any(term in key for term in ['revenue', 'total', 'amount', 'sales'])]
        qty_cols = [col for key, col in columns.items() 
                   if any(term in key for term in ['quantity', 'qty', 'count'])]
        category_cols = [col for key, col in columns.items() 
                        if any(term in key for term in ['category', 'type', 'class'])]
        
        # Revenue chart
        if item_cols and revenue_cols:
            st.markdown("""
            <div class="premium-card">
                <div class="card-title">📈 Revenue Analysis</div>
                <div class="card-subtitle">Top performing items by revenue</div>
            </div>
            """, unsafe_allow_html=True)
            
            item_col = item_cols[0]
            revenue_col = revenue_cols[0]
            
            # Convert to numeric
            df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
            
            # Create chart
            chart_data = df.nlargest(10, revenue_col)
            
            fig = px.bar(
                chart_data,
                x=item_col,
                y=revenue_col,
                title="Top 10 Items by Revenue",
                color=revenue_col,
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family="Inter",
                title_font_size=20,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Category pie chart
        if category_cols and revenue_cols:
            st.markdown("""
            <div class="premium-card">
                <div class="card-title">🥧 Category Performance</div>
                <div class="card-subtitle">Revenue distribution by category</div>
            </div>
            """, unsafe_allow_html=True)
            
            category_col = category_cols[0]
            revenue_col = revenue_cols[0]
            
            # Group by category
            category_data = df.groupby(category_col)[revenue_col].sum().reset_index()
            
            fig = px.pie(
                category_data,
                values=revenue_col,
                names=category_col,
                title="Revenue by Category"
            )
            
            fig.update_layout(
                font_family="Inter",
                title_font_size=20
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_ai_tab(self, df: pd.DataFrame):
        """Render the AI assistant tab"""
        st.markdown("""
        <div class="premium-card">
            <div class="card-title">🤖 AI-Powered Analysis</div>
            <div class="card-subtitle">
                Ask intelligent questions about your restaurant data and get insights powered by advanced pattern recognition.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample questions
        st.markdown("**💡 Try these smart questions:**")
        
        col1, col2 = st.columns(2)
        
        sample_questions = [
            "What are my best performing items?",
            "Which categories drive the most revenue?",
            "What items should I promote more?",
            "How can I optimize my menu pricing?",
            "Which items have the highest profit potential?",
            "What are my underperforming menu items?"
        ]
        
        for i, question in enumerate(sample_questions):
            with col1 if i % 2 == 0 else col2:
                if st.button(question, key=f"sample_q_{i}", use_container_width=True):
                    self._handle_ai_question(question, df)
        
        # Custom question input
        st.markdown("**🎯 Ask your own question:**")
        
        user_question = st.text_area(
            "What would you like to know about your restaurant data?",
            placeholder="Example: How can I increase my profit margins on beverages?",
            height=100,
            key="custom_question"
        )
        
        if st.button("🚀 Get AI Insights", type="primary", key="ai_analyze_button") and user_question.strip():
            self._handle_ai_question(user_question, df)
    
    def _handle_ai_question(self, question: str, df: pd.DataFrame):
        """Handle AI question with smart pattern analysis"""
        # Try Claude AI first (if available)
        ai_result = self.claude_ai.analyze_complex_query(df, question)
        
        if ai_result['available']:
            # Use Claude AI response
            st.success("🧠 Advanced AI Analysis")
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">🤖 {question}</div>
                <div class="insight-text">{ai_result['response']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Use smart pattern fallback
            answer = self._smart_pattern_analysis(question, df)
            
            st.info("🧠 Smart Pattern Analysis")
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">📊 {question}</div>
                <div class="insight-text">{answer}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("💡 Advanced AI analysis with Claude coming soon - currently using intelligent pattern detection")
    
    def _smart_pattern_analysis(self, question: str, df: pd.DataFrame) -> str:
        """Smart pattern-based analysis as fallback"""
        question_lower = question.lower().strip()
        
        # Column detection
        columns = {col.lower().strip(): col for col in df.columns}
        
        item_cols = [col for key, col in columns.items() 
                    if any(term in key for term in ['item', 'product', 'dish', 'name'])]
        revenue_cols = [col for key, col in columns.items() 
                       if any(term in key for term in ['revenue', 'total', 'amount', 'sales'])]
        qty_cols = [col for key, col in columns.items() 
                   if any(term in key for term in ['quantity', 'qty', 'count'])]
        category_cols = [col for key, col in columns.items() 
                        if any(term in key for term in ['category', 'type', 'class'])]
        
        # Best performers analysis
        if any(word in question_lower for word in ['best', 'top', 'performing', 'highest']):
            if item_cols and revenue_cols:
                item_col = item_cols[0]
                revenue_col = revenue_cols[0]
                
                df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
                top_item = df.loc[df[revenue_col].idxmax(), item_col]
                top_revenue = df[revenue_col].max()
                
                return f"**{top_item}** is your top performer with ${top_revenue:,.2f} in revenue. This superstar clearly resonates with customers and deserves prime menu placement. Consider creating variations or combo deals featuring this item to maximize its potential."
        
        # Category analysis
        elif any(word in question_lower for word in ['category', 'categories']):
            if category_cols and revenue_cols:
                category_col = category_cols[0]
                revenue_col = revenue_cols[0]
                
                df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
                category_revenue = df.groupby(category_col)[revenue_col].sum().sort_values(ascending=False)
                
                top_category = category_revenue.index[0]
                top_revenue = category_revenue.iloc[0]
                
                return f"**{top_category}** is your revenue powerhouse, generating ${top_revenue:,.2f}. This category is clearly meeting customer demand. Consider expanding this category with new items or highlighting it more prominently in your marketing and menu design."
        
        # Promotion suggestions
        elif any(word in question_lower for word in ['promote', 'promotion', 'marketing', 'boost']):
            if item_cols and revenue_cols and qty_cols:
                item_col = item_cols[0]
                revenue_col = revenue_cols[0]
                qty_col = qty_cols[0]
                
                df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
                df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce')
                df['avg_price'] = df[revenue_col] / df[qty_col]
                
                # Find high-price, low-volume items
                high_price_threshold = df['avg_price'].quantile(0.75)
                low_volume_threshold = df[qty_col].quantile(0.25)
                
                promotion_candidates = df[
                    (df['avg_price'] >= high_price_threshold) & 
                    (df[qty_col] <= low_volume_threshold)
                ]
                
                if not promotion_candidates.empty:
                    candidate = promotion_candidates.iloc[0][item_col]
                    return f"**{candidate}** is perfect for promotion - it has good pricing but low sales volume. A targeted promotion (happy hour, combo deal, or social media feature) could significantly boost its performance and overall revenue."
        
        # Pricing optimization
        elif any(word in question_lower for word in ['pricing', 'price', 'profit']):
            if item_cols and revenue_cols and qty_cols:
                revenue_col = revenue_cols[0]
                qty_col = qty_cols[0]
                
                df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
                df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce')
                df['avg_price'] = df[revenue_col] / df[qty_col]
                
                avg_price = df['avg_price'].mean()
                highest_priced_item = df.loc[df['avg_price'].idxmax(), item_cols[0]]
                highest_price = df['avg_price'].max()
                
                return f"Your average item price is ${avg_price:.2f}. **{highest_priced_item}** commands ${highest_price:.2f}, proving customers will pay premium prices for quality. Consider gradually testing higher prices on popular items or introducing premium versions of bestsellers."
        
        # Underperforming items
        elif any(word in question_lower for word in ['underperforming', 'worst', 'poor', 'low']):
            if item_cols and revenue_cols:
                item_col = item_cols[0]
                revenue_col = revenue_cols[0]
                
                df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
                bottom_threshold = df[revenue_col].quantile(0.2)
                underperformers = df[df[revenue_col] <= bottom_threshold]
                
                if not underperformers.empty:
                    worst_item = underperformers.loc[underperformers[revenue_col].idxmin(), item_col]
                    return f"**{worst_item}** and {len(underperformers)-1} other items are underperforming. Consider: 1) Recipe improvements, 2) Price adjustments, 3) Better menu positioning, 4) Staff training on upselling, or 5) Replacement with more popular options."
        
        # Default response
        return "I can analyze your data for specific insights about revenue, performance, categories, pricing, and promotions. Try asking more specific questions like 'What are my top 3 revenue generators?' or 'Which items should I consider removing from the menu?'"

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
def main():
    """Application entry point"""
    try:
        app = RestaurantAnalyticsPro()
        app.run()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()