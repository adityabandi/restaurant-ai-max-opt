import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import io
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Restaurant Analytics Pro",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern, clean UI inspired by premium SaaS products
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Reset and base styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: #fafbfc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #1a1f36;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Navigation bar */
    .navbar {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        padding: 1rem 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .navbar-content {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1f36;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .logo-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    
    /* Main container with padding for fixed navbar */
    .main-container {
        padding-top: 80px;
        max-width: 1400px;
        margin: 0 auto;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Hero section */
    .hero-section {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.3; }
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #64748b;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    
    /* Upload section */
    .upload-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: #f8fafc;
        border: 2px dashed #e2e8f0;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
    }
    
    /* Metric cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transform: translateY(-100%);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
    }
    
    .metric-card:hover::before {
        transform: translateY(0);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1f36;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-change {
        font-size: 0.875rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .metric-change.positive {
        color: #10b981;
    }
    
    .metric-change.negative {
        color: #ef4444;
    }
    
    /* Insight cards */
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 1.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
        position: relative;
        border-left: 4px solid transparent;
    }
    
    .insight-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    
    .insight-card.priority-high {
        border-left-color: #ef4444;
    }
    
    .insight-card.priority-medium {
        border-left-color: #f59e0b;
    }
    
    .insight-card.priority-low {
        border-left-color: #10b981;
    }
    
    .insight-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .insight-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .insight-icon.high {
        background: #fee2e2;
        color: #ef4444;
    }
    
    .insight-icon.medium {
        background: #fef3c7;
        color: #f59e0b;
    }
    
    .insight-icon.low {
        background: #d1fae5;
        color: #10b981;
    }
    
    .insight-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1a1f36;
        margin: 0;
    }
    
    .insight-description {
        color: #64748b;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .insight-action {
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        color: #475569;
        border-left: 3px solid #667eea;
    }
    
    /* Charts styling */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1a1f36;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8fafc;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
        border: none;
        font-weight: 500;
    }
    
    .stSuccess {
        background: #d1fae5;
        color: #065f46;
    }
    
    .stError {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid #f0f4ff;
        border-top-color: #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .metric-grid {
            grid-template-columns: 1fr;
        }
        
        .main-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


class DataProcessor:
    """Centralized data processing with robust error handling"""
    
    @staticmethod
    def read_file(file) -> Tuple[bool, pd.DataFrame, str]:
        """Read uploaded file with comprehensive error handling"""
        try:
            file_extension = file.name.split('.')[-1].lower()
            file.seek(0)
            
            if file_extension == 'csv':
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        file.seek(0)
                        df = pd.read_csv(file, encoding=encoding)
                        if not df.empty:
                            return True, df, "CSV file loaded successfully"
                    except:
                        continue
                
                file.seek(0)
                df = pd.read_csv(file, encoding='utf-8', errors='replace')
                return True, df, "CSV file loaded with error correction"
                
            elif file_extension in ['xlsx', 'xls']:
                file.seek(0)
                df = pd.read_excel(file)
                return True, df, "Excel file loaded successfully"
                
            else:
                return False, pd.DataFrame(), f"Unsupported file type: {file_extension}"
                
        except Exception as e:
            return False, pd.DataFrame(), f"Error reading file: {str(e)}"
    
    @staticmethod
    def detect_data_type(df: pd.DataFrame, filename: str) -> str:
        """Intelligently detect the type of data"""
        columns_lower = [col.lower() for col in df.columns]
        filename_lower = filename.lower()
        
        sales_keywords = ['sales', 'revenue', 'transaction', 'order', 'invoice']
        sales_columns = ['item', 'product', 'quantity', 'amount', 'price', 'total']
        
        inventory_keywords = ['inventory', 'stock', 'warehouse']
        inventory_columns = ['item', 'product', 'quantity', 'stock', 'on hand']
        
        for keyword in sales_keywords:
            if keyword in filename_lower:
                return 'sales'
        
        for keyword in inventory_keywords:
            if keyword in filename_lower:
                return 'inventory'
        
        sales_score = sum(1 for col in sales_columns if any(col in c for c in columns_lower))
        inventory_score = sum(1 for col in inventory_columns if any(col in c for c in columns_lower))
        
        if sales_score > inventory_score:
            return 'sales'
        elif inventory_score > sales_score:
            return 'inventory'
        else:
            return 'other'
    
    @staticmethod
    def standardize_columns(df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Standardize column names based on data type"""
        df_copy = df.copy()
        
        column_mappings = {
            'sales': {
                'item': ['item', 'product', 'menu item', 'dish', 'name', 'item name', 'product name'],
                'quantity': ['quantity', 'qty', 'count', 'units', 'amount sold'],
                'price': ['price', 'unit price', 'cost', 'amount', 'sale price'],
                'total': ['total', 'revenue', 'total amount', 'sales', 'gross'],
                'date': ['date', 'time', 'timestamp', 'order date', 'transaction date'],
                'category': ['category', 'type', 'group', 'class', 'department']
            },
            'inventory': {
                'item': ['item', 'product', 'sku', 'name', 'item name', 'product name'],
                'quantity': ['quantity', 'qty', 'stock', 'on hand', 'available', 'count'],
                'cost': ['cost', 'unit cost', 'price', 'value'],
                'category': ['category', 'type', 'group', 'class', 'department']
            }
        }
        
        mappings = column_mappings.get(data_type, {})
        
        for standard_name, variations in mappings.items():
            for col in df_copy.columns:
                col_lower = col.lower().strip()
                if col_lower in variations:
                    df_copy.rename(columns={col: standard_name}, inplace=True)
                    break
        
        return df_copy
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data"""
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        numeric_columns = ['quantity', 'price', 'total', 'cost']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        string_columns = ['item', 'category']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(['nan', 'None', ''], pd.NA)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df


class InsightGenerator:
    """Generate actionable insights from data"""
    
    @staticmethod
    def analyze_sales_data(df: pd.DataFrame) -> List[Dict]:
        """Generate insights from sales data"""
        insights = []
        
        if df.empty or 'item' not in df.columns:
            return insights
        
        # Top performers
        if 'total' in df.columns or 'price' in df.columns:
            revenue_col = 'total' if 'total' in df.columns else 'price'
            top_items = df.groupby('item')[revenue_col].sum().nlargest(5)
            
            if not top_items.empty:
                top_item = top_items.index[0]
                top_revenue = top_items.iloc[0]
                
                insights.append({
                    'type': 'top_performer',
                    'priority': 'high',
                    'icon': '🌟',
                    'title': f'{top_item} is crushing it!',
                    'description': f'This superstar is bringing in ${top_revenue:,.2f} in revenue. That\'s your money maker right there!',
                    'recommendation': 'Keep this item front and center on your menu. Maybe even create variations or combos featuring it.',
                    'value': top_revenue
                })
        
        # Low performers
        if 'quantity' in df.columns:
            item_counts = df.groupby('item')['quantity'].sum()
            bottom_items = item_counts[item_counts < item_counts.mean() * 0.2]
            
            if not bottom_items.empty:
                insights.append({
                    'type': 'low_performer',
                    'priority': 'medium',
                    'icon': '📉',
                    'title': f'{len(bottom_items)} items need attention',
                    'description': f'These items are selling way below average. Items like {", ".join(bottom_items.index[:2])} might be costing you more than they\'re worth.',
                    'recommendation': 'Time for tough decisions - revamp these dishes or remove them to streamline your menu.',
                    'items': list(bottom_items.index[:3])
                })
        
        # Category analysis
        if 'category' in df.columns and 'total' in df.columns:
            category_revenue = df.groupby('category')['total'].sum().sort_values(ascending=False)
            
            if len(category_revenue) > 0:
                top_category = category_revenue.index[0]
                insights.append({
                    'type': 'category_leader',
                    'priority': 'medium',
                    'icon': '🏆',
                    'title': f'{top_category} is your golden category',
                    'description': f'This category alone is generating ${category_revenue.iloc[0]:,.2f}. Your customers clearly love it!',
                    'recommendation': 'Double down on this category. Add more options and highlight it in your marketing.',
                    'value': category_revenue.iloc[0]
                })
        
        # Trend analysis (if we have dates)
        if 'date' in df.columns and 'total' in df.columns:
            df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
            daily_revenue = df.groupby('weekday')['total'].sum()
            
            if not daily_revenue.empty:
                best_day = daily_revenue.idxmax()
                worst_day = daily_revenue.idxmin()
                
                insights.append({
                    'type': 'weekly_pattern',
                    'priority': 'low',
                    'icon': '📅',
                    'title': f'{best_day}s are your power days',
                    'description': f'You make {(daily_revenue[best_day] / daily_revenue[worst_day] - 1) * 100:.0f}% more on {best_day}s compared to {worst_day}s.',
                    'recommendation': f'Staff up for {best_day}s and run specials on {worst_day}s to boost traffic.',
                    'best_day': best_day,
                    'worst_day': worst_day
                })
        
        return insights
    
    @staticmethod
    def analyze_inventory_data(df: pd.DataFrame) -> List[Dict]:
        """Generate insights from inventory data"""
        insights = []
        
        if df.empty or 'item' not in df.columns:
            return insights
        
        if 'quantity' in df.columns:
            low_stock = df[df['quantity'] < 10]
            
            if not low_stock.empty:
                critical_items = low_stock.nsmallest(5, 'quantity')
                insights.append({
                    'type': 'low_stock',
                    'priority': 'high',
                    'icon': '⚠️',
                    'title': 'Stock emergency!',
                    'description': f'{len(low_stock)} items are running dangerously low. {critical_items.iloc[0]["item"]} has only {critical_items.iloc[0]["quantity"]} left!',
                    'recommendation': 'Place orders NOW for these items to avoid disappointing customers and losing sales.',
                    'items': list(critical_items['item'])
                })
        
        if 'quantity' in df.columns and 'cost' in df.columns:
            df['value'] = df['quantity'] * df['cost']
            total_value = df['value'].sum()
            
            # Find overstocked expensive items
            high_value_items = df[df['value'] > df['value'].mean() * 2]
            
            if not high_value_items.empty:
                insights.append({
                    'type': 'cash_tied_up',
                    'priority': 'medium',
                    'icon': '💰',
                    'title': 'Cash trapped in inventory',
                    'description': f'You have ${high_value_items["value"].sum():,.2f} tied up in just {len(high_value_items)} items. That\'s money that could be working for you!',
                    'recommendation': 'Run promotions on these high-value items to free up cash flow.',
                    'value': high_value_items["value"].sum()
                })
        
        return insights
    
    @staticmethod
    def analyze_cross_data(sales_df: pd.DataFrame, inventory_df: pd.DataFrame) -> List[Dict]:
        """Generate insights from multiple data sources"""
        insights = []
        
        if sales_df.empty or inventory_df.empty:
            return insights
        
        if 'item' in sales_df.columns and 'item' in inventory_df.columns:
            if 'quantity' in sales_df.columns:
                top_sellers = sales_df.groupby('item')['quantity'].sum().nlargest(10)
                
                for item in top_sellers.index:
                    inv_match = inventory_df[inventory_df['item'].str.lower() == item.lower()]
                    
                    if not inv_match.empty and 'quantity' in inv_match.columns:
                        stock_level = inv_match['quantity'].iloc[0]
                        sales_velocity = top_sellers[item]
                        days_remaining = stock_level / (sales_velocity / 30) if sales_velocity > 0 else 999
                        
                        if days_remaining < 7:
                            insights.append({
                                'type': 'stockout_risk',
                                'priority': 'high',
                                'icon': '🚨',
                                'title': f'{item} stockout alert!',
                                'description': f'You\'ll run out in {days_remaining:.0f} days! This is one of your best sellers.',
                                'recommendation': f'Order at least {int(sales_velocity * 2)} units TODAY to avoid losing sales.',
                                'item': item,
                                'days_remaining': days_remaining
                            })
        
        return insights


class RestaurantAnalyticsApp:
    def __init__(self):
        self.processor = DataProcessor()
        self.insights_generator = InsightGenerator()
        
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = {}
        if 'insights' not in st.session_state:
            st.session_state.insights = []
        if 'show_upload' not in st.session_state:
            st.session_state.show_upload = True
    
    def run(self):
        """Main application flow"""
        self.show_navbar()
        
        # Main container
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        if st.session_state.show_upload:
            self.show_hero_section()
            self.show_upload_section()
        else:
            self.show_dashboard()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_navbar(self):
        """Display navigation bar"""
        st.markdown("""
        <div class="navbar">
            <div class="navbar-content">
                <div class="logo">
                    <div class="logo-icon">🍽️</div>
                    <span>Restaurant Analytics Pro</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_hero_section(self):
        """Display hero section"""
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">Turn Your Data Into Profit</h1>
            <p class="hero-subtitle">
                Upload your restaurant data and get instant insights that save you thousands every month.
                <br>Join 500+ restaurants already boosting their profits.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def show_upload_section(self):
        """File upload interface"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            <div class="upload-section">
                <h2 style="margin-bottom: 1.5rem;">📊 Upload Your Data</h2>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_files = st.file_uploader(
                "Drop your files here or click to browse",
                type=['csv', 'xlsx', 'xls'],
                accept_multiple_files=True,
                help="You can upload multiple files - sales data, inventory reports, anything!"
            )
            
            if uploaded_files:
                self.process_uploaded_files(uploaded_files)
        
        with col2:
            st.markdown("""
            <div class="upload-section" style="text-align: center;">
                <h3 style="margin-bottom: 1rem;">🚀 Try It Out</h3>
                <p style="color: #64748b; margin-bottom: 1.5rem;">See what insights look like with sample data</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("LOAD DEMO DATA", use_container_width=True):
                self.load_demo_data()
    
    def process_uploaded_files(self, files):
        """Process uploaded files with beautiful progress"""
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        for i, file in enumerate(files):
            # Show progress
            progress = (i + 1) / len(files)
            progress_placeholder.markdown(f"""
            <div style="background: #f0f4ff; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600; color: #667eea;">Processing {file.name}</span>
                    <span style="color: #64748b;">{int(progress * 100)}%</span>
                </div>
                <div style="background: #e0e7ff; border-radius: 4px; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                                height: 100%; width: {progress * 100}%; transition: width 0.3s ease;">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Read and process file
            success, df, message = self.processor.read_file(file)
            
            if success:
                data_type = self.processor.detect_data_type(df, file.name)
                df = self.processor.standardize_columns(df, data_type)
                df = self.processor.clean_data(df)
                
                st.session_state.uploaded_files[file.name] = {
                    'data': df,
                    'type': data_type,
                    'rows': len(df),
                    'columns': list(df.columns)
                }
                
                status_placeholder.success(f"✅ {file.name}: {len(df)} rows of {data_type} data")
            else:
                status_placeholder.error(f"❌ {file.name}: {message}")
        
        # Generate insights
        self.generate_all_insights()
        
        # Clear placeholders and switch to dashboard
        progress_placeholder.empty()
        status_placeholder.empty()
        st.session_state.show_upload = False
        st.rerun()
    
    def load_demo_data(self):
        """Load sample restaurant data"""
        # Sample sales data
        sales_data = pd.DataFrame({
            'item': ['Classic Burger', 'Caesar Salad', 'Margherita Pizza', 'Grilled Salmon', 'Chicken Wings'],
            'quantity': [45, 12, 28, 22, 35],
            'price': [16.99, 14.99, 18.99, 24.99, 12.99],
            'total': [764.55, 179.88, 531.72, 549.78, 454.65],
            'category': ['Entrees', 'Salads', 'Pizza', 'Entrees', 'Appetizers']
        })
        
        # Sample inventory data  
        inventory_data = pd.DataFrame({
            'item': ['Classic Burger', 'Caesar Salad', 'Margherita Pizza', 'Grilled Salmon', 'Chicken Wings'],
            'quantity': [53, 7, 42, 18, 105],
            'cost': [5.75, 4.25, 6.50, 9.95, 4.80],
            'category': ['Entrees', 'Salads', 'Pizza', 'Entrees', 'Appetizers']
        })
        
        st.session_state.uploaded_files = {
            'demo_sales.csv': {'data': sales_data, 'type': 'sales', 'rows': len(sales_data), 'columns': list(sales_data.columns)},
            'demo_inventory.csv': {'data': inventory_data, 'type': 'inventory', 'rows': len(inventory_data), 'columns': list(inventory_data.columns)}
        }
        
        self.generate_all_insights()
        st.session_state.show_upload = False
        st.success("🎉 Demo data loaded! Check out your insights.")
        st.rerun()
    
    def generate_all_insights(self):
        """Generate insights from all uploaded data"""
        all_insights = []
        sales_dfs = []
        inventory_dfs = []
        
        # Separate data by type
        for filename, file_data in st.session_state.uploaded_files.items():
            df = file_data['data']
            data_type = file_data['type']
            
            if data_type == 'sales':
                all_insights.extend(self.insights_generator.analyze_sales_data(df))
                sales_dfs.append(df)
            elif data_type == 'inventory':
                all_insights.extend(self.insights_generator.analyze_inventory_data(df))
                inventory_dfs.append(df)
        
        # Cross-analysis if we have both types
        if sales_dfs and inventory_dfs:
            for sales_df in sales_dfs:
                for inv_df in inventory_dfs:
                    all_insights.extend(self.insights_generator.analyze_cross_data(sales_df, inv_df))
        
        st.session_state.insights = all_insights
    
    def show_dashboard(self):
        """Main dashboard view"""
        # Header with back button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Upload New Data"):
                st.session_state.show_upload = True
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <h2 style="margin: 0; color: #1a1f36;">
                📊 Analyzing {len(st.session_state.uploaded_files)} files
            </h2>
            """, unsafe_allow_html=True)
        
        # File summary
        total_rows = sum(f['rows'] for f in st.session_state.uploaded_files.values())
        file_types = [f['type'] for f in st.session_state.uploaded_files.values()]
        
        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.uploaded_files)}</div>
                <div class="metric-label">Files Processed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_rows:,}</div>
                <div class="metric-label">Total Records</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(set(file_types))}</div>
                <div class="metric-label">Data Types</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.insights)}</div>
                <div class="metric-label">Insights Generated</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["💡 Insights", "📊 Data Overview", "❓ Ask Questions"])
        
        with tab1:
            self.show_insights()
        
        with tab2:
            self.show_data_overview()
        
        with tab3:
            self.show_query_interface()
    
    def show_insights(self):
        """Display generated insights"""
        if not st.session_state.insights:
            st.info("No insights generated yet. Upload some data to get started!")
            return
        
        # Sort insights by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_insights = sorted(
            st.session_state.insights, 
            key=lambda x: priority_order.get(x.get('priority', 'medium'), 1)
        )
        
        for insight in sorted_insights:
            priority = insight.get('priority', 'medium')
            icon = insight.get('icon', '💡')
            title = insight.get('title', 'Insight')
            description = insight.get('description', '')
            recommendation = insight.get('recommendation', '')
            
            st.markdown(f"""
            <div class="insight-card priority-{priority}">
                <div class="insight-header">
                    <div class="insight-icon {priority}">{icon}</div>
                    <div class="insight-title">{title}</div>
                </div>
                <div class="insight-description">{description}</div>
                <div class="insight-action">💡 {recommendation}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def show_data_overview(self):
        """Show data overview and charts"""
        for filename, file_data in st.session_state.uploaded_files.items():
            df = file_data['data']
            data_type = file_data['type']
            
            st.markdown(f"""
            <div class="chart-container">
                <div class="chart-title">📄 {filename} ({data_type.title()} Data)</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show sample data
            st.dataframe(df.head(10), use_container_width=True)
            
            # Create charts based on data type
            if data_type == 'sales' and 'item' in df.columns:
                if 'total' in df.columns:
                    top_items = df.groupby('item')['total'].sum().nlargest(10)
                    if not top_items.empty:
                        fig = px.bar(
                            x=top_items.values,
                            y=top_items.index,
                            orientation='h',
                            title="Top 10 Revenue Generators",
                            labels={'x': 'Revenue ($)', 'y': 'Item'}
                        )
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                
                if 'quantity' in df.columns:
                    top_quantity = df.groupby('item')['quantity'].sum().nlargest(10)
                    if not top_quantity.empty:
                        fig = px.bar(
                            x=top_quantity.values,
                            y=top_quantity.index,
                            orientation='h',
                            title="Top 10 Best Sellers by Quantity",
                            labels={'x': 'Quantity Sold', 'y': 'Item'}
                        )
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
            
            elif data_type == 'inventory' and 'item' in df.columns and 'quantity' in df.columns:
                # Inventory levels chart
                fig = px.bar(
                    df.nsmallest(15, 'quantity'),
                    x='quantity',
                    y='item',
                    orientation='h',
                    title="Items with Lowest Stock Levels",
                    labels={'quantity': 'Stock Quantity', 'item': 'Item'}
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    def show_query_interface(self):
        """Natural language query interface"""
        st.markdown("""
        <div class="upload-section">
            <h3>🤔 Ask Questions About Your Data</h3>
            <p style="color: #64748b;">Ask me anything about your restaurant data in plain English!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample questions
        st.markdown("**Try these questions:**")
        
        sample_questions = [
            "What are my best selling items?",
            "Which items make the most money?",
            "What items are running low in stock?",
            "Which category performs best?",
            "Show me underperforming menu items"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(sample_questions):
            with cols[i % 2]:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    answer = self.answer_question(question)
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-title">Answer:</div>
                        <div class="insight-description">{answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Custom question input
        user_question = st.text_area(
            "Or ask your own question:",
            placeholder="Example: Which items should I promote more?",
            height=100
        )
        
        if st.button("Get Answer", type="primary") and user_question:
            answer = self.answer_question(user_question)
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Answer:</div>
                <div class="insight-description">{answer}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def answer_question(self, question: str) -> str:
        """Answer questions about the data"""
        question_lower = question.lower()
        
        # Get all sales data
        sales_data = []
        inventory_data = []
        
        for file_data in st.session_state.uploaded_files.values():
            if file_data['type'] == 'sales':
                sales_data.append(file_data['data'])
            elif file_data['type'] == 'inventory':
                inventory_data.append(file_data['data'])
        
        if not sales_data and not inventory_data:
            return "I don't have any data to analyze yet. Please upload some files first!"
        
        # Combine sales data
        all_sales = pd.concat(sales_data) if sales_data else pd.DataFrame()
        all_inventory = pd.concat(inventory_data) if inventory_data else pd.DataFrame()
        
        # Best selling items
        if any(phrase in question_lower for phrase in ['best selling', 'top selling', 'most popular']):
            if not all_sales.empty and 'quantity' in all_sales.columns and 'item' in all_sales.columns:
                top_items = all_sales.groupby('item')['quantity'].sum().nlargest(5)
                items_list = [f"{item}: {qty} sold" for item, qty in top_items.items()]
                return f"Your top selling items are:<br>• " + "<br>• ".join(items_list)
            return "I need sales data with quantities to answer this question."
        
        # Revenue leaders
        if any(phrase in question_lower for phrase in ['most money', 'revenue', 'highest earning']):
            if not all_sales.empty and 'total' in all_sales.columns and 'item' in all_sales.columns:
                top_revenue = all_sales.groupby('item')['total'].sum().nlargest(5)
                items_list = [f"{item}: ${revenue:.2f}" for item, revenue in top_revenue.items()]
                return f"Your biggest money makers are:<br>• " + "<br>• ".join(items_list)
            return "I need sales data with revenue amounts to answer this question."
        
        # Low stock
        if any(phrase in question_lower for phrase in ['low stock', 'running low', 'inventory']):
            if not all_inventory.empty and 'quantity' in all_inventory.columns and 'item' in all_inventory.columns:
                low_stock = all_inventory[all_inventory['quantity'] < 20].nsmallest(5, 'quantity')
                if not low_stock.empty:
                    items_list = [f"{row['item']}: {row['quantity']} left" for _, row in low_stock.iterrows()]
                    return f"Items running low on stock:<br>• " + "<br>• ".join(items_list)
                return "Good news! All your items have healthy stock levels (above 20 units)."
            return "I need inventory data to check stock levels."
        
        # Category performance
        if any(phrase in question_lower for phrase in ['category', 'best category']):
            if not all_sales.empty and 'category' in all_sales.columns and 'total' in all_sales.columns:
                cat_revenue = all_sales.groupby('category')['total'].sum().sort_values(ascending=False)
                items_list = [f"{cat}: ${revenue:.2f}" for cat, revenue in cat_revenue.items()]
                return f"Category performance by revenue:<br>• " + "<br>• ".join(items_list)
            return "I need sales data with categories to answer this question."
        
        # Underperforming items
        if any(phrase in question_lower for phrase in ['underperforming', 'worst', 'slow moving']):
            if not all_sales.empty and 'quantity' in all_sales.columns and 'item' in all_sales.columns:
                item_performance = all_sales.groupby('item')['quantity'].sum()
                underperformers = item_performance.nsmallest(5)
                items_list = [f"{item}: only {qty} sold" for item, qty in underperformers.items()]
                return f"Items that need attention:<br>• " + "<br>• ".join(items_list) + "<br><br>💡 Consider removing these or running promotions to boost sales."
            return "I need sales data with quantities to identify underperforming items."
        
        return "I'm not sure how to answer that question. Try asking about best sellers, revenue, inventory levels, or categories!"


# Run the app
if __name__ == "__main__":
    app = RestaurantAnalyticsApp()
    app.run()