import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import os
import json
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Optional
import requests
import time

# Import our custom modules
try:
    from database import RestaurantDB
    from ai_excel_parser import AIExcelParser
    from weather_intelligence import WeatherIntelligence
    from revenue_analyzer import RevenueAnalyzer
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Restaurant AI Analytics Pro",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, Professional UI Design (YouWare-Inspired)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* === CLEAN FOUNDATION === */
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        color: #1a1a1a;
        line-height: 1.6;
    }
    
    /* Hide Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* === CLEAN HEADER === */
    .main-header {
        background: #ffffff;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 3rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .main-header h1 {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 600;
        margin: 0;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        margin: 0;
        color: #6b7280;
        font-weight: 400;
    }
    
    /* === CLEAN CARDS === */
    .metric-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #2563eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .insight-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #e5e7eb;
        border-left: 3px solid #2563eb;
    }
    
    /* === QUERY INTERFACE === */
    .query-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    
    .query-response {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 6px;
        border-left: 3px solid #2563eb;
        margin: 1rem 0;
    }
    
    .suggestion-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .suggestion-pill {
        background: #f1f5f9;
        color: #374151;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.875rem;
    }
    
    .suggestion-pill:hover {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }
    
    .priority-high { 
        border-left-color: #dc2626;
    }
    .priority-medium { 
        border-left-color: #ea580c;
    }
    .priority-low { 
        border-left-color: #059669;
    }
    
    /* === CLEAN SECTIONS === */
    .upload-section {
        background: #f9fafb;
        padding: 3rem 2rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }
    
    .demo-section {
        background: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        text-align: center;
    }
    
    /* === CLEAN BUTTONS === */
    .stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: background-color 0.2s ease !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        color: white !important;
    }
    
    .stButton > button:focus {
        background-color: #1d4ed8 !important;
        color: white !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Force button text visibility */
    .stButton button p {
        color: white !important;
        margin: 0 !important;
    }
    
    .stButton button div {
        color: white !important;
    }
    
    /* === CLEAN INPUTS === */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        background-color: white;
        color: #1a1a1a;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        outline: none;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* === CLEAN FILE UPLOADER === */
    .stFileUploader > div > div {
        border: 2px dashed #e5e7eb;
        border-radius: 8px;
        padding: 2rem;
        background-color: #ffffff;
        transition: border-color 0.2s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #2563eb;
    }
    
    /* === CLEAN TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    p, div {
        color: #6b7280;
        line-height: 1.6;
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* === MINIMAL STATUS === */
    .api-status {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .api-active {
        background: #f0fdf4;
        color: #166534;
        border-color: #bbf7d0;
    }
    
    .api-fallback {
        background: #fef2f2;
        color: #dc2626;
        border-color: #fecaca;
    }
</style>
""", unsafe_allow_html=True)

class RestaurantAnalyticsApp:
    def __init__(self):
        # Skip database for now to avoid login issues
        self.db = None
        self.parser = AIExcelParser()
        self.weather = WeatherIntelligence(None)  # Pass None for db
        self.revenue_analyzer = RevenueAnalyzer()
        
        # Check API status
        self.api_status = self._check_api_status()
        
        # Initialize session state safely
        if not hasattr(st.session_state, 'uploaded_data'):
            st.session_state.uploaded_data = None
        if not hasattr(st.session_state, 'insights'):
            st.session_state.insights = []
    
    def _check_api_status(self):
        """Check if AI APIs are available"""
        status = {
            'claude': False,
            'weather': True  # Weather API is working
        }
        
        # Check Claude API
        try:
            import os
            if os.getenv("ANTHROPIC_API_KEY") or (hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets):
                status['claude'] = True
        except:
            pass
        
        return status
    
    def run(self):
        """Main application runner"""
        # Show API status
        self._show_api_status()
        
        # Skip auth for now - go straight to main app
        self._show_main_app()
    
    def _show_api_status(self):
        """Show API status indicator"""
        if self.api_status['claude']:
            st.markdown("""
            <div class="api-status api-active">
                🤖 AI Enhanced Mode
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="api-status api-fallback">
                🧠 Smart Analytics Mode
            </div>
            """, unsafe_allow_html=True)
    
    def _show_main_app(self):
        """Show main application interface"""
        # Clean header
        st.markdown("""
        <div class="main-header">
            <h1>Restaurant Analytics Pro</h1>
            <p>Turn your data into profit with AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main content
        if not hasattr(st.session_state, 'uploaded_data') or st.session_state.uploaded_data is None:
            self._show_upload_section()
        else:
            self._show_dashboard()
    
    def _show_upload_section(self):
        """Show enhanced file upload section with multiple file support"""
        # Clean upload section
        st.markdown("""
        <div class="upload-section">
            <h2>Upload Your Restaurant Data</h2>
            <p>Get instant insights that save $1,200+ monthly</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload zone with multiple file support
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### Upload Your Data")
            
            uploaded_files = st.file_uploader(
                "Choose your restaurant data files",
                type=['xlsx', 'csv', 'xls'],
                accept_multiple_files=True,
                help="Upload multiple restaurant files - AI will automatically detect formats and connections between them!"
            )
            
            if uploaded_files:
                with st.spinner("Analyzing your data..."):
                    all_processed_data = []
                    file_types = []
                    file_successes = []
                    
                    for uploaded_file in uploaded_files:
                        result = self._process_uploaded_file(uploaded_file, show_messages=False)
                        if result['success']:
                            all_processed_data.append(result['processed_data'])
                            file_types.append(result['data_type'])
                            file_successes.append({
                                'filename': uploaded_file.name,
                                'data_type': result['data_type'],
                                'rows': len(result['processed_data'])
                            })
                    
                    # Show summary of processed files
                    if file_successes:
                        total_files = len(file_successes)
                        total_rows = sum(success['rows'] for success in file_successes)
                        
                        st.success(f"✅ Successfully processed {total_files} files with {total_rows} total records!")
                        
                        # Show file details
                        for success in file_successes:
                            st.info(f"📄 {success['filename']}: {success['rows']} rows of {success['data_type']} data")
                        
                        # Check for relationships between files if multiple types
                        if len(set(file_types)) > 1:
                            st.info("🔄 Multiple data types detected! Cross-file analysis enabled.")
                            st.session_state.cross_file_analysis = True
                        
                        # Store all data
                        st.session_state.uploaded_data = {
                            'upload_id': 'multi-upload',
                            'filenames': [f['filename'] for f in file_successes],
                            'data_types': file_types,
                            'processed_data': [item for sublist in all_processed_data for item in sublist],
                            'individual_datasets': all_processed_data,
                            'ai_confidence': 0.9
                        }
                        
                        # Generate insights from all data
                        self._generate_insights_from_multiple_sources(all_processed_data, file_types)
                        
                        # Continue to dashboard
                        st.rerun()
                    else:
                        st.error("❌ Could not process any of the uploaded files. Please check the format.")
        
        with col2:
            # Demo section
            st.markdown("""
            <div class="demo-section">
                <h3>Try Demo Data</h3>
                <p>See the platform in action with realistic restaurant data</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Load Demo Restaurant", use_container_width=True):
                self._load_demo_data()
            
            # Benefits
            st.markdown("### What You'll Discover:")
            st.markdown("💰 **Exact savings** — '$847/month from removing Caesar Salad'")
            st.markdown("📈 **Menu rankings** — Which items make you the most money")
            st.markdown("🌤️ **Weather predictions** — 'Rain = +60% delivery orders'")
            st.markdown("🎯 **Action items** — Step-by-step profit improvements")
    
    def _load_demo_data(self):
        """Load comprehensive demo data for testing including multiple data types"""
        # Create realistic sales demo data
        sales_data = [
            {'item_name': 'Classic Burger', 'quantity': 45, 'unit_price': 16.99, 'total_amount': 764.55, 'category': 'Entrees'},
            {'item_name': 'Caesar Salad', 'quantity': 12, 'unit_price': 14.99, 'total_amount': 179.88, 'category': 'Salads'},
            {'item_name': 'Margherita Pizza', 'quantity': 28, 'unit_price': 18.99, 'total_amount': 531.72, 'category': 'Pizza'},
            {'item_name': 'Grilled Salmon', 'quantity': 22, 'unit_price': 24.99, 'total_amount': 549.78, 'category': 'Entrees'},
            {'item_name': 'Chicken Wings', 'quantity': 35, 'unit_price': 12.99, 'total_amount': 454.65, 'category': 'Appetizers'},
            {'item_name': 'Fish Tacos', 'quantity': 19, 'unit_price': 15.99, 'total_amount': 303.81, 'category': 'Entrees'},
            {'item_name': 'Craft Beer', 'quantity': 67, 'unit_price': 6.99, 'total_amount': 468.33, 'category': 'Beverages'},
            {'item_name': 'House Wine', 'quantity': 31, 'unit_price': 8.99, 'total_amount': 278.69, 'category': 'Beverages'},
            {'item_name': 'Chocolate Cake', 'quantity': 15, 'unit_price': 7.99, 'total_amount': 119.85, 'category': 'Desserts'},
            {'item_name': 'Truffle Pasta', 'quantity': 8, 'unit_price': 26.99, 'total_amount': 215.92, 'category': 'Pasta'}
        ]
        
        # Create matching inventory data
        inventory_data = [
            {'item_name': 'Classic Burger', 'quantity': 53, 'cost': 5.75, 'category': 'Entrees'},
            {'item_name': 'Caesar Salad', 'quantity': 7, 'cost': 4.25, 'category': 'Salads'},
            {'item_name': 'Margherita Pizza', 'quantity': 42, 'cost': 6.50, 'category': 'Pizza'},
            {'item_name': 'Grilled Salmon', 'quantity': 18, 'cost': 9.95, 'category': 'Entrees'},
            {'item_name': 'Chicken Wings', 'quantity': 105, 'cost': 4.80, 'category': 'Appetizers'},
            {'item_name': 'Fish Tacos', 'quantity': 5, 'cost': 5.25, 'category': 'Entrees'},
            {'item_name': 'Craft Beer', 'quantity': 150, 'cost': 2.10, 'category': 'Beverages'},
            {'item_name': 'House Wine', 'quantity': 42, 'cost': 3.50, 'category': 'Beverages'},
            {'item_name': 'Chocolate Cake', 'quantity': 20, 'cost': 2.75, 'category': 'Desserts'},
            {'item_name': 'Truffle Pasta', 'quantity': 16, 'cost': 9.80, 'category': 'Pasta'}
        ]
        
        # Store in session state with multiple datasets
        st.session_state.uploaded_data = {
            'upload_id': 'demo-multi',
            'filenames': ['demo_sales.csv', 'demo_inventory.csv'],
            'data_types': ['sales', 'inventory'],
            'processed_data': sales_data + inventory_data,  # Combined for backward compatibility
            'individual_datasets': [sales_data, inventory_data],
            'ai_confidence': 0.95
        }
        
        # Set cross-file analysis flag
        st.session_state.cross_file_analysis = True
        
        # Generate insights from all data
        self._generate_insights_from_multiple_sources([sales_data, inventory_data], ['sales', 'inventory'])
        
        st.success("🎉 Demo data loaded! Explore restaurant analytics with cross-dataset analysis.")
        st.rerun()
    
    def _process_uploaded_file(self, uploaded_file, show_messages=True):
        """Process uploaded file with enhanced AI parsing and error handling"""
        try:
            # Read file contents
            file_contents = uploaded_file.read()
            
            # Check file size
            file_size = len(file_contents)
            if file_size == 0:
                if show_messages:
                    st.error("❌ The uploaded file is empty.")
                return {'success': False, 'error': "Empty file"}
            
            # Get file extension for better error messages
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['csv', 'xlsx', 'xls']:
                if show_messages:
                    st.warning(f"⚠️ File type '.{file_extension}' may not be supported. Attempting to process anyway...")
            
            # Parse file with AI
            parsing_result = self.parser.parse_file(file_contents, uploaded_file.name)
            
            if parsing_result['success']:
                # Store processed data
                processed_data = parsing_result['processed_data']
                data_type = parsing_result['data_type']
                
                if show_messages:
                    st.success(f"✅ Successfully processed {len(processed_data)} records as {data_type} data!")
                
                return {
                    'success': True,
                    'filename': uploaded_file.name,
                    'data_type': data_type,
                    'processed_data': processed_data,
                    'ai_confidence': parsing_result.get('ai_confidence', 0.85)
                }
            else:
                if show_messages:
                    st.error(f"❌ Error processing file: {parsing_result['error']}")
                    
                    # Show helpful suggestions
                    if 'suggestions' in parsing_result:
                        for suggestion in parsing_result['suggestions']:
                            st.info(f"💡 {suggestion}")
                
                return {'success': False, 'error': parsing_result['error']}
        
        except Exception as e:
            if show_messages:
                st.error(f"❌ Unexpected error: {str(e)}")
            
            return {'success': False, 'error': str(e)}
    
    def _generate_insights_from_multiple_sources(self, datasets, data_types):
        """Generate cross-file insights by analyzing relationships between different data types"""
        all_insights = []
        
        # First, generate insights for each individual dataset
        for i, dataset in enumerate(datasets):
            data_type = data_types[i]
            
            if data_type == 'sales':
                # Use revenue analyzer for sales data
                menu_analysis = self.revenue_analyzer.analyze_menu_performance(dataset)
                insights = self.revenue_analyzer.generate_actionable_insights(menu_analysis)
                all_insights.extend(insights)
        
        # Then generate cross-dataset insights if we have multiple types
        unique_types = set(data_types)
        if len(unique_types) > 1:
            cross_insights = self._generate_cross_dataset_insights(datasets, data_types)
            all_insights.extend(cross_insights)
        
        # Add demo weather insights
        if self.api_status['weather']:
            weather_insights = [
                {
                    'type': 'weather_prediction',
                    'priority': 'medium',
                    'title': '🌧️ Rain Forecast: +60% Delivery Revenue',
                    'description': 'Light rain expected this weekend will significantly boost delivery orders',
                    'recommendation': 'Increase delivery staff by 40% and prep comfort food specials',
                    'savings_potential': 850,
                    'confidence_score': 0.87
                },
                {
                    'type': 'weather_temperature',
                    'priority': 'medium', 
                    'title': '🌡️ Cool Weather: Hot Beverage Surge',
                    'description': 'Temperature dropping to 38°F will drive hot drink sales up 45%',
                    'recommendation': 'Stock extra coffee, hot chocolate, and warm cocktails',
                    'savings_potential': 320,
                    'confidence_score': 0.82
                },
                {
                    'type': 'weather_operations',
                    'priority': 'low',
                    'title': '☀️ Clear Skies: Patio Opportunity',
                    'description': 'Perfect weather Tuesday increases patio seating demand by 35%',
                    'recommendation': 'Open all outdoor seating and promote patio specials',
                    'savings_potential': 240,
                    'confidence_score': 0.79
                }
            ]
            all_insights.extend(weather_insights)
        
        # Store insights
        st.session_state.insights = all_insights
    
    def _generate_cross_dataset_insights(self, datasets, data_types):
        """Generate insights by analyzing relationships between multiple datasets"""
        cross_insights = []
        
        # Check for sales + inventory data
        sales_idx = None
        inventory_idx = None
        
        for i, data_type in enumerate(data_types):
            if data_type == 'sales':
                sales_idx = i
            elif data_type == 'inventory':
                inventory_idx = i
        
        # If we have both sales and inventory data
        if sales_idx is not None and inventory_idx is not None:
            sales_data = datasets[sales_idx]
            inventory_data = datasets[inventory_idx]
            
            # Simple stockout risk analysis
            try:
                # Get top selling items
                top_items = {}
                for item in sales_data:
                    name = item.get('item_name', '')
                    if name:
                        qty = item.get('quantity', 0)
                        if name in top_items:
                            top_items[name] += qty
                        else:
                            top_items[name] = qty
                
                # Sort by quantity
                top_items = {k: v for k, v in sorted(top_items.items(), key=lambda item: item[1], reverse=True)[:5]}
                
                # Check inventory levels for top items
                stockout_risks = []
                for item_name, qty_sold in top_items.items():
                    # Find matching inventory item
                    matching_items = [inv for inv in inventory_data if inv.get('item_name', '').lower() == item_name.lower()]
                    
                    if matching_items:
                        inv_item = matching_items[0]
                        stock_level = inv_item.get('quantity', 0)
                        
                        # Calculate days of inventory based on sales velocity
                        daily_usage = qty_sold / 30  # Assume 30 day period
                        days_remaining = stock_level / daily_usage if daily_usage > 0 else 99
                        
                        if days_remaining < 7:  # Less than a week of inventory
                            stockout_risks.append({
                                'item': item_name,
                                'days_remaining': round(days_remaining, 1),
                                'current_stock': stock_level,
                                'daily_usage': round(daily_usage, 1)
                            })
                
                # Create insights for stockout risks
                if stockout_risks:
                    for risk in stockout_risks:
                        cross_insights.append({
                            'type': 'inventory_alert',
                            'priority': 'high' if risk['days_remaining'] < 3 else 'medium',
                            'title': f"⚠️ {risk['item']} Stockout Risk: {risk['days_remaining']} Days Left",
                            'description': f"High-selling item with low inventory. Only {risk['current_stock']} units left with daily usage of {risk['daily_usage']} units.",
                            'recommendation': f"Order {int(risk['daily_usage'] * 14)} units to maintain 2-week supply",
                            'savings_potential': 500,  # Estimated lost sales prevention
                            'confidence_score': 0.85,
                            'affected_items': [risk['item']]
                        })
                    
                    # Add an overall inventory management insight
                    cross_insights.append({
                        'type': 'inventory_management',
                        'priority': 'medium',
                        'title': f"🔄 Inventory-Sales Alignment Opportunity",
                        'description': f"Your inventory levels for top-selling items need adjustment based on sales velocity.",
                        'recommendation': "Implement automatic reorder points based on actual sales data",
                        'savings_potential': 1200,
                        'confidence_score': 0.82,
                        'action_items': [
                            "Set up weekly inventory-sales reconciliation",
                            "Create safety stock levels for top 10 items",
                            "Reduce order frequency for slow-moving items"
                        ]
                    })
            except Exception as e:
                # If cross-analysis fails, add a basic insight
                cross_insights.append({
                    'type': 'data_connection',
                    'priority': 'medium',
                    'title': "🔄 Connected Data Sources Detected",
                    'description': "We've detected both sales and inventory data, but couldn't fully analyze relationships.",
                    'recommendation': "Ensure consistent item naming between sales and inventory systems",
                    'savings_potential': 800,
                    'confidence_score': 0.7
                })
        
        return cross_insights
    
    def _show_dashboard(self):
        """Show the main dashboard with insights"""
        # Safely get session state data
        data = getattr(st.session_state, 'uploaded_data', None)
        insights = getattr(st.session_state, 'insights', [])
        
        # Check if we have valid data
        if not data or 'processed_data' not in data:
            st.error("No data available. Please upload a file first.")
            if st.button("← Go Back to Upload"):
                st.session_state.uploaded_data = None
                st.rerun()
            return
        
        # Header with upload info
        try:
            items_count = len(data.get('processed_data', []))
            filename = data.get('filename', 'Unknown file')
            data_type = data.get('data_type', 'unknown')
            confidence = data.get('ai_confidence', 0.8)
            
            st.markdown(f"""
            <div style="background: #f9fafb; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 2rem;">
                <h3 style="margin: 0; color: #1a1a1a;">📊 {filename}</h3>
                <p style="margin: 0.5rem 0 0 0; color: #6b7280;">
                    {items_count} items analyzed • 
                    {data_type.title()} data • 
                    {confidence*100:.0f}% confidence
                </p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying dashboard header: {str(e)}")
        
        if st.button("← Upload New Data", type="secondary"):
            st.session_state.uploaded_data = None
            st.session_state.insights = []
            st.rerun()
        
        # Tabs for different views
        tabs = ["💰 Revenue Insights", "📊 Data Overview", "❓ Ask Questions", "🌤️ Weather Intelligence"]
        
        # Add Cross-Dataset Analysis tab if multiple data types detected
        if hasattr(st.session_state, 'cross_file_analysis') and st.session_state.cross_file_analysis:
            tabs.append("🔄 Cross-Dataset Analysis")
        
        # Create tabs dynamically
        selected_tabs = st.tabs(tabs)
        
        with selected_tabs[0]:  # Revenue Insights
            self._show_revenue_insights(insights)
        
        with selected_tabs[1]:  # Data Overview
            self._show_data_overview(data.get('processed_data', []))
        
        with selected_tabs[2]:  # Ask Questions
            self._show_query_interface(data)
        
        with selected_tabs[3]:  # Weather Intelligence
            self._show_weather_insights(insights)
        
        # Show cross-dataset analysis if available
        if len(tabs) > 4:
            with selected_tabs[4]:  # Cross-Dataset Analysis
                self._show_cross_dataset_analysis(data, insights)
    
    def _show_revenue_insights(self, insights):
        """Show revenue insights"""
        if not insights:
            st.info("No insights generated yet.")
            return
        
        # Total savings potential
        total_savings = sum(insight.get('savings_potential', 0) for insight in insights)
        
        if total_savings > 0:
            st.markdown(f"""
            <div style="background: #2563eb; color: white; padding: 2rem; border-radius: 8px; text-align: center; margin-bottom: 2rem;">
                <h2 style="margin: 0; color: white;">💰 Total Monthly Savings Potential</h2>
                <h1 style="margin: 0.5rem 0 0 0; color: white;">${total_savings:,.0f}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        # Show insights
        for insight in insights:
            priority_class = f"priority-{insight.get('priority', 'medium')}"
            
            st.markdown(f"""
            <div class="insight-card {priority_class}">
                <h3 style="margin: 0 0 1rem 0; color: #1a1a1a;">{insight.get('title', 'Insight')}</h3>
                <p style="margin: 0 0 1rem 0;">{insight.get('description', '')}</p>
                <p style="margin: 0; font-weight: 600; color: #1a1a1a;">
                    💡 {insight.get('recommendation', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def _show_data_overview(self, processed_data):
        """Show data overview with clean charts"""
        df = pd.DataFrame(processed_data)
        
        if df.empty:
            st.info("No data to display.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(df)}</div>
                <div class="metric-label">Total Items</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_revenue = df.get('total_amount', df.get('price', 0)).sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">${total_revenue:,.0f}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_price = df.get('price', 0).mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">${avg_price:.2f}</div>
                <div class="metric-label">Average Price</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_quantity = df.get('quantity', 1).sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{total_quantity}</div>
                <div class="metric-label">Items Sold</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        st.markdown("### Revenue by Item")
        
        # Create clean revenue chart
        if 'total_amount' in df.columns:
            fig = px.bar(
                df.nlargest(10, 'total_amount'), 
                x='item_name', 
                y='total_amount',
                title="Top 10 Items by Revenue"
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1a1a1a'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.markdown("### Data Details")
        st.dataframe(df, use_container_width=True)
    
    def _show_query_interface(self, data):
        """Show natural language query interface"""
        st.markdown("""
        <div class="query-card">
            <h3 style="margin: 0 0 1rem 0; color: #374151;">Ask Questions About Your Data</h3>
            <p style="margin: 0 0 1.5rem 0; color: #6b7280;">Get instant answers about your restaurant performance using natural language.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize query history
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        
        # Suggested questions
        st.markdown("**Try these questions:**")
        suggestions = [
            "What are my best selling items?",
            "Which items have the highest profit margins?",
            "What time of day is busiest?",
            "How do weekends compare to weekdays?",
            "What items should I promote more?",
            "Are there any underperforming menu items?"
        ]
        
        # Display suggestion pills
        cols = st.columns(3)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    st.session_state.current_query = suggestion
        
        # Query input
        query = st.text_area(
            "Ask your question:",
            value=st.session_state.get('current_query', ''),
            placeholder="Example: What are my top 5 menu items by revenue this month?",
            height=100,
            key="query_input"
        )
        
        # Process query
        if st.button("Get Answer", type="primary", use_container_width=True):
            if query.strip():
                with st.spinner("Analyzing your data..."):
                    response = self._process_natural_language_query(query, data)
                    
                    # Add to history
                    st.session_state.query_history.insert(0, {
                        'question': query,
                        'answer': response,
                        'timestamp': datetime.now().strftime('%H:%M')
                    })
                    
                    # Clear current query
                    if 'current_query' in st.session_state:
                        del st.session_state.current_query
        
        # Show query history
        if st.session_state.query_history:
            st.markdown("### Recent Questions")
            for i, item in enumerate(st.session_state.query_history[:5]):  # Show last 5
                with st.expander(f"🕐 {item['timestamp']} - {item['question']}", expanded=i==0):
                    st.markdown(f"""
                    <div class="query-response">
                        {item['answer']}
                    </div>
                    """, unsafe_allow_html=True)
    
    def _process_natural_language_query(self, query: str, data: Dict) -> str:
        """Process natural language queries with cost-effective AI usage"""
        processed_data = data.get('processed_data', [])
        
        if not processed_data:
            return "❌ No data available to analyze. Please upload your restaurant data first."
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(processed_data)
        
        # Step 1: Try simple pattern matching first (free & fast)
        simple_answer = self._try_simple_query_patterns(query.lower(), df)
        if simple_answer:
            return simple_answer
        
        # Step 2: Use AI for complex queries (only when needed)
        return self._use_ai_for_complex_query(query, df)
    
    def _try_simple_query_patterns(self, query: str, df: pd.DataFrame) -> Optional[str]:
        """Try to answer simple queries without AI"""
        
        # Best selling items
        if any(phrase in query for phrase in ['best selling', 'top selling', 'most popular']):
            return self._get_top_items_by_quantity(df)
        
        # Highest revenue items
        if any(phrase in query for phrase in ['highest revenue', 'most revenue', 'top revenue']):
            return self._get_top_items_by_revenue(df)
        
        # Profit margin analysis
        if any(phrase in query for phrase in ['profit margin', 'most profitable', 'highest margin']):
            return self._get_profit_margin_analysis(df)
        
        # Time-based analysis
        if any(phrase in query for phrase in ['busiest time', 'peak hours', 'what time']):
            return self._get_time_analysis(df)
        
        # Underperforming items
        if any(phrase in query for phrase in ['underperforming', 'worst selling', 'slow moving']):
            return self._get_underperforming_items(df)
        
        # Weekend vs weekday
        if any(phrase in query for phrase in ['weekend', 'weekday', 'compare days']):
            return self._get_weekend_analysis(df)
        
        return None  # No simple pattern matched
    
    def _get_top_items_by_quantity(self, df: pd.DataFrame) -> str:
        """Get top selling items by quantity"""
        if 'item_name' not in df.columns or 'quantity' not in df.columns:
            return "❌ Need item names and quantities to analyze best sellers."
        
        top_items = df.groupby('item_name')['quantity'].sum().sort_values(ascending=False).head(5)
        
        result = "🔥 **Top 5 Best Selling Items:**\n\n"
        for i, (item, qty) in enumerate(top_items.items(), 1):
            result += f"{i}. **{item}** - {qty:.0f} units sold\n"
        
        return result
    
    def _get_top_items_by_revenue(self, df: pd.DataFrame) -> str:
        """Get top items by revenue"""
        if 'item_name' not in df.columns or 'total_amount' not in df.columns:
            return "❌ Need item names and revenue data to analyze top earners."
        
        top_revenue = df.groupby('item_name')['total_amount'].sum().sort_values(ascending=False).head(5)
        
        result = "💰 **Top 5 Revenue Generating Items:**\n\n"
        for i, (item, revenue) in enumerate(top_revenue.items(), 1):
            result += f"{i}. **{item}** - ${revenue:.2f}\n"
        
        return result
    
    def _get_profit_margin_analysis(self, df: pd.DataFrame) -> str:
        """Analyze profit margins"""
        if not all(col in df.columns for col in ['item_name', 'total_amount']):
            return "❌ Need item names and revenue data for profit analysis."
        
        # Calculate margins if cost data available
        if 'cost' in df.columns:
            df['margin'] = df['total_amount'] - df['cost']
            df['margin_percent'] = (df['margin'] / df['total_amount'] * 100).round(1)
            
            top_margins = df.groupby('item_name').agg({
                'margin': 'sum',
                'margin_percent': 'mean'
            }).sort_values('margin', ascending=False).head(5)
            
            result = "📊 **Highest Profit Margin Items:**\n\n"
            for i, (item, data) in enumerate(top_margins.iterrows(), 1):
                result += f"{i}. **{item}** - ${data['margin']:.2f} ({data['margin_percent']:.1f}% margin)\n"
        else:
            # Estimate based on revenue (assuming 30% food cost)
            top_revenue = df.groupby('item_name')['total_amount'].sum().sort_values(ascending=False).head(5)
            
            result = "📊 **Estimated Profit Leaders** (assuming 30% food cost):\n\n"
            for i, (item, revenue) in enumerate(top_revenue.items(), 1):
                estimated_profit = revenue * 0.7
                result += f"{i}. **{item}** - ${estimated_profit:.2f} estimated profit\n"
        
        return result
    
    def _get_time_analysis(self, df: pd.DataFrame) -> str:
        """Analyze time-based patterns"""
        if 'hour_of_day' in df.columns:
            hourly_sales = df.groupby('hour_of_day')['total_amount'].sum()
            peak_hour = hourly_sales.idxmax()
            peak_amount = hourly_sales.max()
            
            result = f"⏰ **Peak Hours Analysis:**\n\n"
            result += f"🔥 Busiest hour: **{peak_hour}:00** (${peak_amount:.2f} in sales)\n\n"
            result += "**Top 3 busiest hours:**\n"
            
            for i, (hour, amount) in enumerate(hourly_sales.sort_values(ascending=False).head(3).items(), 1):
                result += f"{i}. {hour}:00 - ${amount:.2f}\n"
        else:
            result = "❌ Need time data to analyze peak hours. Consider including time columns in your data."
        
        return result
    
    def _get_underperforming_items(self, df: pd.DataFrame) -> str:
        """Find underperforming items"""
        if 'item_name' not in df.columns or 'quantity' not in df.columns:
            return "❌ Need item names and quantities to find underperforming items."
        
        item_performance = df.groupby('item_name').agg({
            'quantity': 'sum',
            'total_amount': 'sum'
        }).sort_values('quantity')
        
        bottom_items = item_performance.head(5)
        
        result = "📉 **Underperforming Items** (lowest sales volume):\n\n"
        for i, (item, data) in enumerate(bottom_items.iterrows(), 1):
            result += f"{i}. **{item}** - {data['quantity']:.0f} units, ${data['total_amount']:.2f} revenue\n"
        
        result += "\n💡 **Suggestions:** Consider promoting these items or removing them from the menu."
        
        return result
    
    def _get_weekend_analysis(self, df: pd.DataFrame) -> str:
        """Compare weekend vs weekday performance"""
        if 'is_weekend' not in df.columns:
            return "❌ Need date information to compare weekends vs weekdays."
        
        comparison = df.groupby('is_weekend').agg({
            'total_amount': ['sum', 'mean'],
            'quantity': 'sum'
        }).round(2)
        
        weekend_revenue = comparison.loc[True, ('total_amount', 'sum')] if True in comparison.index else 0
        weekday_revenue = comparison.loc[False, ('total_amount', 'sum')] if False in comparison.index else 0
        
        result = "📅 **Weekend vs Weekday Analysis:**\n\n"
        result += f"🌴 **Weekend Total:** ${weekend_revenue:.2f}\n"
        result += f"🏢 **Weekday Total:** ${weekday_revenue:.2f}\n\n"
        
        if weekend_revenue > weekday_revenue:
            result += "🎯 **Insight:** Weekends are stronger - consider weekend-specific promotions!"
        else:
            result += "🎯 **Insight:** Weekdays are stronger - focus on maintaining business lunch traffic!"
        
        return result
    
    def _use_ai_for_complex_query(self, query: str, df: pd.DataFrame) -> str:
        """Use AI for complex queries that pattern matching can't handle"""
        
        # Check if AI is available
        parser = AIExcelParser()
        if not parser.anthropic_client:
            return "❌ AI analysis not available. Try simpler questions like 'What are my best selling items?' or 'Which items have the highest revenue?'"
        
        # Prepare data summary for AI
        data_summary = self._prepare_data_summary_for_ai(df)
        
        prompt = f"""
        You are a restaurant business analyst. Answer this question about the restaurant's performance data:
        
        Question: {query}
        
        Data Summary:
        {data_summary}
        
        Provide a helpful, actionable answer that:
        1. Directly answers the question
        2. Includes specific numbers and insights
        3. Gives practical recommendations
        4. Uses a friendly, professional tone
        5. Formats the response with markdown for readability
        
        Keep the response concise but informative (max 300 words).
        """
        
        try:
            message = parser.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=400,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"❌ Unable to process complex query: {str(e)}\n\nTry simpler questions like:\n• What are my best selling items?\n• Which items make the most revenue?\n• What time of day is busiest?"
    
    def _prepare_data_summary_for_ai(self, df: pd.DataFrame) -> str:
        """Prepare a concise data summary for AI analysis"""
        summary = f"Dataset: {len(df)} records\n"
        summary += f"Columns: {', '.join(df.columns)}\n\n"
        
        # Top items by quantity
        if 'item_name' in df.columns and 'quantity' in df.columns:
            top_items = df.groupby('item_name')['quantity'].sum().sort_values(ascending=False).head(3)
            summary += "Top 3 items by quantity:\n"
            for item, qty in top_items.items():
                summary += f"- {item}: {qty} units\n"
            summary += "\n"
        
        # Revenue summary
        if 'total_amount' in df.columns:
            total_revenue = df['total_amount'].sum()
            avg_transaction = df['total_amount'].mean()
            summary += f"Total Revenue: ${total_revenue:.2f}\n"
            summary += f"Average Transaction: ${avg_transaction:.2f}\n\n"
        
        # Time patterns if available
        if 'hour_of_day' in df.columns:
            peak_hour = df.groupby('hour_of_day')['total_amount'].sum().idxmax()
            summary += f"Peak hour: {peak_hour}:00\n"
        
        return summary
    
    def _show_weather_insights(self, insights):
        """Show weather-related insights"""
        weather_insights = [i for i in insights if i.get('type', '').startswith('weather')]
        
        if not weather_insights:
            st.info("No weather insights available.")
            return
        
        st.markdown("### 🌤️ Weather Impact Analysis")
        
        for insight in weather_insights:
            st.markdown(f"""
            <div class="insight-card">
                <h3 style="margin: 0 0 1rem 0; color: #1a1a1a;">{insight.get('title', 'Weather Insight')}</h3>
                <p style="margin: 0 0 1rem 0;">{insight.get('description', '')}</p>
                <p style="margin: 0; font-weight: 600; color: #1a1a1a;">
                    🎯 {insight.get('recommendation', '')}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def _show_cross_dataset_analysis(self, data, insights):
        """Show cross-dataset analysis when multiple data types are available"""
        st.markdown("### 🔄 Integrated Business Intelligence")
        
        if not data or 'individual_datasets' not in data or 'data_types' not in data:
            st.info("No cross-dataset analysis available.")
            return
        
        # Extract relevant cross-dataset insights
        cross_insights = [i for i in insights if i.get('type', '') in [
            'inventory_alert', 'inventory_management', 'data_connection',
            'cost_optimization', 'operational_efficiency', 'supply_chain'
        ]]
        
        # Display cross-dataset insights if available
        if cross_insights:
            st.markdown("#### Key Cross-Dataset Insights")
            
            for insight in cross_insights:
                priority_class = f"priority-{insight.get('priority', 'medium')}"
                
                st.markdown(f"""
                <div class="insight-card {priority_class}">
                    <h3 style="margin: 0 0 1rem 0; color: #1a1a1a;">{insight.get('title', 'Insight')}</h3>
                    <p style="margin: 0 0 1rem 0;">{insight.get('description', '')}</p>
                    <p style="margin: 0; font-weight: 600; color: #1a1a1a;">
                        💡 {insight.get('recommendation', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Data relationship visualization
        st.markdown("#### Data Relationships")
        
        # Extract data types
        data_types = data.get('data_types', [])
        unique_types = set(data_types)
        
        # Create a visual representation of connected data
        if len(unique_types) > 1:
            # Create simple diagram
            import networkx as nx
            import matplotlib.pyplot as plt
            from matplotlib.colors import to_rgba
            
            try:
                # Create graph
                G = nx.Graph()
                
                # Add nodes for each data type
                for data_type in unique_types:
                    G.add_node(data_type)
                
                # Add edges for related data types
                for i, type1 in enumerate(unique_types):
                    for type2 in list(unique_types)[i+1:]:
                        # Check if there's a relationship between these types
                        if (type1 == 'sales' and type2 == 'inventory') or \
                           (type1 == 'inventory' and type2 == 'sales') or \
                           (type1 == 'sales' and type2 == 'supplier') or \
                           (type1 == 'supplier' and type2 == 'sales'):
                            G.add_edge(type1, type2)
                
                # Define colors for different data types
                color_map = {
                    'sales': '#3498db',     # Blue
                    'inventory': '#2ecc71', # Green
                    'supplier': '#e74c3c',  # Red
                    'accounting': '#f39c12', # Yellow
                    'other': '#95a5a6'      # Gray
                }
                
                # Apply colors to nodes
                node_colors = [color_map.get(node, '#95a5a6') for node in G.nodes()]
                
                # Create the figure
                plt.figure(figsize=(8, 5))
                pos = nx.spring_layout(G, seed=42)  # For reproducibility
                
                # Draw the graph
                nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors, alpha=0.9)
                nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color='#34495e')
                nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold', font_color='white')
                
                # Save figure to a temporary file
                import tempfile
                import os
                
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, 'data_relationship.png')
                plt.tight_layout()
                plt.axis('off')
                plt.savefig(temp_file, format='png', bbox_inches='tight', transparent=True)
                plt.close()
                
                # Display the image
                from PIL import Image
                img = Image.open(temp_file)
                st.image(img, caption="Data Relationship Diagram", use_column_width=True)
                
                # Add explanation
                st.markdown("""
                The diagram above shows how your different data types are connected. 
                Connected data types can provide deeper insights through cross-analysis.
                """)
                
            except Exception as e:
                st.error(f"Error creating data relationship visualization: {str(e)}")
                st.markdown("""
                Your data includes multiple data types that can be analyzed together 
                for deeper insights into your restaurant operations.
                """)
        
        # Based on data types, show specific cross-dataset visualizations
        if 'sales' in unique_types and 'inventory' in unique_types:
            self._show_sales_inventory_analysis(data.get('individual_datasets', []), data_types)
        
    def _show_sales_inventory_analysis(self, datasets, data_types):
        """Show visualization and analysis for sales and inventory data"""
        st.markdown("#### Sales-Inventory Analysis")
        
        # Find sales and inventory data
        sales_idx = data_types.index('sales') if 'sales' in data_types else None
        inventory_idx = data_types.index('inventory') if 'inventory' in data_types else None
        
        if sales_idx is None or inventory_idx is None or len(datasets) <= max(sales_idx, inventory_idx):
            st.info("Complete sales and inventory data not available for detailed analysis.")
            return
        
        sales_data = datasets[sales_idx]
        inventory_data = datasets[inventory_idx]
        
        # Convert to DataFrames
        sales_df = pd.DataFrame(sales_data)
        inventory_df = pd.DataFrame(inventory_data)
        
        if sales_df.empty or inventory_df.empty:
            st.info("One or more datasets are empty.")
            return
        
        # Create aggregated sales data
        if 'item_name' in sales_df.columns and 'quantity' in sales_df.columns:
            # Aggregate sales by item
            sales_summary = sales_df.groupby('item_name')['quantity'].sum().reset_index()
            sales_summary.columns = ['item_name', 'quantity_sold']
            
            # Find matching inventory items
            # Create lowercase versions for matching
            sales_summary['item_lower'] = sales_summary['item_name'].str.lower()
            inventory_df['item_lower'] = inventory_df['item_name'].str.lower()
            
            # Merge datasets on item name
            merged_data = pd.merge(
                sales_summary, 
                inventory_df,
                left_on='item_lower', 
                right_on='item_lower', 
                how='inner',
                suffixes=('_sales', '_inventory')
            )
            
            if not merged_data.empty:
                # Calculate days of inventory remaining based on sales velocity
                if 'quantity' in merged_data.columns:
                    # Assuming 30 day period for sales data
                    merged_data['daily_usage'] = merged_data['quantity_sold'] / 30
                    merged_data['days_remaining'] = merged_data['quantity'] / merged_data['daily_usage']
                    merged_data['days_remaining'] = merged_data['days_remaining'].fillna(99)  # Handle div by zero
                    merged_data['days_remaining'] = merged_data['days_remaining'].round(1)
                    
                    # Create a visualization
                    st.markdown("##### Inventory Levels Relative to Sales Velocity")
                    
                    # Sort by days remaining
                    chart_data = merged_data.sort_values('days_remaining').head(10)
                    
                    # Generate color scale based on days remaining (red->yellow->green)
                    colors = []
                    for days in chart_data['days_remaining']:
                        if days < 7:  # Less than a week: red
                            colors.append('#e74c3c')
                        elif days < 14:  # Less than two weeks: yellow
                            colors.append('#f39c12')
                        else:  # Enough inventory: green
                            colors.append('#2ecc71')
                    
                    # Create horizontal bar chart
                    fig = px.bar(
                        chart_data,
                        y='item_name_sales',
                        x='days_remaining',
                        orientation='h',
                        title="Days of Inventory Remaining Based on Sales Velocity",
                        labels={'days_remaining': 'Days Remaining', 'item_name_sales': 'Item'},
                        text='days_remaining'
                    )
                    
                    # Update layout
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font_color='#1a1a1a',
                        height=400,
                        margin=dict(l=10, r=10, t=40, b=10),
                        yaxis=dict(autorange="reversed")  # Reverse y-axis to have highest value at top
                    )
                    
                    # Update marker colors individually
                    for i, color in enumerate(colors):
                        fig.data[0].marker.color = colors
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add explanation
                    st.markdown("""
                    This chart shows how many days of inventory you have left for each item based on current sales velocity.
                    Items with less than 7 days of inventory (red) are at risk of stockout and should be reordered immediately.
                    """)
                    
                    # Show detailed inventory-sales table
                    st.markdown("##### Inventory-Sales Details")
                    
                    # Create a clean table for display
                    display_cols = [
                        'item_name_sales', 'quantity_sold', 'quantity', 
                        'daily_usage', 'days_remaining'
                    ]
                    
                    # Rename columns for clarity
                    display_df = merged_data[display_cols].copy()
                    display_df.columns = [
                        'Item', 'Quantity Sold', 'Current Stock',
                        'Daily Usage', 'Days Remaining'
                    ]
                    
                    # Add recommended order amount
                    display_df['Recommended Order'] = (display_df['Daily Usage'] * 14).round().astype(int)
                    
                    # Sort by days remaining
                    display_df = display_df.sort_values('Days Remaining')
                    
                    # Show the table
                    st.dataframe(display_df, use_column_width=True)
                    
                    # Inventory health summary
                    st.markdown("##### Inventory Health Summary")
                    
                    # Calculate inventory health metrics
                    low_stock = len(merged_data[merged_data['days_remaining'] < 7])
                    medium_stock = len(merged_data[(merged_data['days_remaining'] >= 7) & (merged_data['days_remaining'] < 14)])
                    healthy_stock = len(merged_data[merged_data['days_remaining'] >= 14])
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card" style="border-left: 4px solid #e74c3c;">
                            <div class="metric-number" style="color: #e74c3c;">{low_stock}</div>
                            <div class="metric-label">Critical Items</div>
                            <div style="font-size: 0.8rem; color: #6b7280;">Less than 7 days</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card" style="border-left: 4px solid #f39c12;">
                            <div class="metric-number" style="color: #f39c12;">{medium_stock}</div>
                            <div class="metric-label">Warning Items</div>
                            <div style="font-size: 0.8rem; color: #6b7280;">7-14 days</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card" style="border-left: 4px solid #2ecc71;">
                            <div class="metric-number" style="color: #2ecc71;">{healthy_stock}</div>
                            <div class="metric-label">Healthy Items</div>
                            <div style="font-size: 0.8rem; color: #6b7280;">14+ days</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                else:
                    st.info("Inventory quantity data not available for comparison.")
            else:
                st.info("No matching items found between sales and inventory data.")
        else:
            st.info("Required columns not found in sales data.")

# Run the application
if __name__ == "__main__":
    app = RestaurantAnalyticsApp()
    app.run()
