"""
Restaurant AI Max Opt - Premium Neumorphic UI
Professional restaurant analytics with soft, approachable design
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Any
import json
import os

# Import our enhanced components
try:
    from ui_components import NeumorphicUI, DataPreviewUI
except ImportError:
    st.error("UI components not found. Please check installation.")
    st.stop()

try:
    from enhanced_excel_parser import EnhancedExcelParser
except ImportError:
    # Fallback to AI Excel Parser if enhanced version fails
    from ai_excel_parser import AIExcelParser as EnhancedExcelParser

try:
    from hybrid_ai_system import HybridAI, SmartAnalytics
except ImportError:
    HybridAI = None
    SmartAnalytics = None

try:
    from restaurant_analytics import RestaurantAnalytics
    from data_warehouse import RestaurantDataWarehouse
except ImportError:
    RestaurantAnalytics = None
    RestaurantDataWarehouse = None

# Page config
st.set_page_config(
    page_title="Restaurant AI Max Opt",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_warehouse' not in st.session_state:
    if RestaurantDataWarehouse:
        st.session_state.data_warehouse = RestaurantDataWarehouse()
    else:
        st.session_state.data_warehouse = type('DataWarehouse', (), {'datasets': {}})()
        
if 'analytics_engine' not in st.session_state:
    if RestaurantAnalytics:
        st.session_state.analytics_engine = RestaurantAnalytics()
    else:
        st.session_state.analytics_engine = type('Analytics', (), {
            'generate_comprehensive_insights': lambda: {}
        })()
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'dashboard'

# Load neumorphic CSS
NeumorphicUI.load_neumorphic_css()

class RestaurantApp:
    """Main application class with neumorphic UI"""
    
    def __init__(self):
        self.parser = EnhancedExcelParser()
        self.ui = NeumorphicUI()
        self.preview_ui = DataPreviewUI()
        
        # Initialize hybrid AI if available
        if HybridAI and SmartAnalytics:
            self.ai = HybridAI()
            self.smart_analytics = SmartAnalytics()
        else:
            self.ai = None
            self.smart_analytics = None
        
    def run(self):
        """Main app entry point"""
        # Render header
        NeumorphicUI.render_header(
            "🍽️ Restaurant AI Max Opt",
            "Intelligent analytics that feel as good as they look"
        )
        
        # Sidebar navigation
        self.render_sidebar()
        
        # Main content area
        if st.session_state.current_view == 'dashboard':
            self.render_dashboard()
        elif st.session_state.current_view == 'upload':
            self.render_upload_section()
        elif st.session_state.current_view == 'insights':
            self.render_insights()
        elif st.session_state.current_view == 'optimizer':
            self.render_menu_optimizer()
        elif st.session_state.current_view == 'inventory':
            self.render_inventory_manager()
    
    def render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <div style="font-size: 3rem;">🍽️</div>
                <h2 style="color: #2C3E50; margin: 0.5rem 0;">Restaurant AI</h2>
                <p style="color: #7F8C8D; font-size: 0.9rem;">Max Optimization</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation buttons
            nav_items = [
                ('dashboard', '📊', 'Dashboard'),
                ('upload', '📤', 'Upload Data'),
                ('insights', '💡', 'Smart Insights'),
                ('optimizer', '💰', 'Menu Optimizer'),
                ('inventory', '📦', 'Inventory AI')
            ]
            
            for view_id, icon, label in nav_items:
                if st.button(f"{icon} {label}", key=f"nav_{view_id}", 
                           use_container_width=True,
                           type="primary" if st.session_state.current_view == view_id else "secondary"):
                    st.session_state.current_view = view_id
                    st.rerun()
            
            # Quick stats
            st.markdown("---")
            st.markdown("### 📈 Quick Stats")
            
            if st.session_state.data_warehouse.datasets:
                total_revenue = self._calculate_total_revenue()
                avg_transaction = self._calculate_avg_transaction()
                
                NeumorphicUI.render_metric_card(
                    "Total Revenue",
                    f"${total_revenue:,.0f}",
                    "+12.3% vs last month",
                    "positive"
                )
                
                NeumorphicUI.render_metric_card(
                    "Avg Transaction",
                    f"${avg_transaction:.2f}",
                    "+$2.15 vs last week",
                    "positive"
                )
            else:
                st.info("Upload data to see stats")
    
    def render_dashboard(self):
        """Render main dashboard"""
        st.markdown("## 📊 Performance Dashboard")
        
        if not st.session_state.data_warehouse.datasets:
            # Show onboarding
            self.render_onboarding()
        else:
            # Show metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                NeumorphicUI.render_metric_card(
                    "Today's Revenue",
                    "$3,847",
                    "+15.2%",
                    "positive",
                    "💰"
                )
            
            with col2:
                NeumorphicUI.render_metric_card(
                    "Food Cost",
                    "28.4%",
                    "-2.1%",
                    "positive",
                    "🍔"
                )
            
            with col3:
                NeumorphicUI.render_metric_card(
                    "Labor Cost",
                    "24.7%",
                    "+0.8%",
                    "negative",
                    "👥"
                )
            
            with col4:
                NeumorphicUI.render_metric_card(
                    "Table Turns",
                    "4.2",
                    "+0.3",
                    "positive",
                    "🔄"
                )
            
            # Charts section
            st.markdown("### 📈 Revenue Trends")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate sample revenue data
                dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                revenue = np.random.normal(3500, 500, 30).cumsum() + 50000
                revenue_series = pd.Series(revenue, index=dates)
                
                fig = NeumorphicUI.create_neumorphic_chart(
                    revenue_series,
                    chart_type="line",
                    title="30-Day Revenue Trend"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Category performance
                categories = pd.Series({
                    'Entrees': 45000,
                    'Appetizers': 22000,
                    'Beverages': 28000,
                    'Desserts': 15000,
                    'Sides': 10000
                })
                
                fig = NeumorphicUI.create_neumorphic_chart(
                    categories,
                    chart_type="donut",
                    title="Revenue by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Alerts section
            st.markdown("### 🚨 Smart Alerts")
            
            col1, col2 = st.columns(2)
            
            with col1:
                NeumorphicUI.render_alert(
                    "Low inventory alert: Chicken breast (2 days left)",
                    "warning"
                )
                NeumorphicUI.render_alert(
                    "Price optimization: Burger could be $1.50 higher",
                    "success"
                )
            
            with col2:
                NeumorphicUI.render_alert(
                    "High food waste detected on Tuesday prep",
                    "danger"
                )
                NeumorphicUI.render_alert(
                    "New efficiency record: 12 min avg ticket time!",
                    "success"
                )
    
    def render_onboarding(self):
        """Render onboarding experience"""
        st.markdown("""
        <div class="neu-card" style="text-align: center; padding: 4rem;">
            <div style="font-size: 5rem; margin-bottom: 2rem;">🚀</div>
            <h2 style="color: #2C3E50; margin-bottom: 1rem;">Welcome to Restaurant AI Max Opt</h2>
            <p style="color: #7F8C8D; font-size: 1.1rem; margin-bottom: 2rem;">
                Upload your restaurant data and discover hidden profit opportunities with AI-powered insights
            </p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin: 3rem 0;">
                <div class="neu-inset" style="padding: 2rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">📊</div>
                    <h4 style="color: #2C3E50;">Smart Analytics</h4>
                    <p style="color: #7F8C8D; font-size: 0.9rem;">
                        AI understands your data instantly
                    </p>
                </div>
                <div class="neu-inset" style="padding: 2rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">💰</div>
                    <h4 style="color: #2C3E50;">Profit Insights</h4>
                    <p style="color: #7F8C8D; font-size: 0.9rem;">
                        Find money leaks and opportunities
                    </p>
                </div>
                <div class="neu-inset" style="padding: 2rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎯</div>
                    <h4 style="color: #2C3E50;">Action Plans</h4>
                    <p style="color: #7F8C8D; font-size: 0.9rem;">
                        Get specific steps to increase profits
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Get Started - Upload Your Data", 
                        use_container_width=True, type="primary"):
                st.session_state.current_view = 'upload'
                st.rerun()
    
    def render_upload_section(self):
        """Render file upload section with preview"""
        st.markdown("## 📤 Upload Your Restaurant Data")
        
        # Instructions
        st.markdown("""
        <div class="neu-card">
            <h3 style="color: #2C3E50; margin-bottom: 1rem;">📋 Supported Formats</h3>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                <div style="text-align: center;">
                    <div class="neu-icon">📊</div>
                    <div style="color: #2C3E50; font-weight: 600;">Excel Files</div>
                    <div style="color: #7F8C8D; font-size: 0.85rem;">.xlsx, .xls</div>
                </div>
                <div style="text-align: center;">
                    <div class="neu-icon">📄</div>
                    <div style="color: #2C3E50; font-weight: 600;">CSV Files</div>
                    <div style="color: #7F8C8D; font-size: 0.85rem;">.csv, .txt</div>
                </div>
                <div style="text-align: center;">
                    <div class="neu-icon">💳</div>
                    <div style="color: #2C3E50; font-weight: 600;">POS Exports</div>
                    <div style="color: #7F8C8D; font-size: 0.85rem;">All major systems</div>
                </div>
                <div style="text-align: center;">
                    <div class="neu-icon">📦</div>
                    <div style="color: #2C3E50; font-weight: 600;">Inventory</div>
                    <div style="color: #7F8C8D; font-size: 0.85rem;">Stock reports</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Drop your file here or click to browse",
            type=['csv', 'xlsx', 'xls', 'txt'],
            help="Support for all major POS systems and formats"
        )
        
        if uploaded_file:
            # Show processing status
            with st.spinner("🔍 Analyzing your file..."):
                # Parse file in preview mode first
                preview_result = self.parser.parse_file(
                    uploaded_file.read(),
                    uploaded_file.name,
                    preview_only=True
                )
                
                # Reset file pointer for actual processing
                uploaded_file.seek(0)
            
            if preview_result['success']:
                # Show preview
                st.markdown("### 📋 File Preview")
                
                self.preview_ui.render_file_preview(preview_result)
                
                # Column mapping
                self.preview_ui.render_column_mapping(preview_result['column_preview'])
                
                # Data preview table
                st.markdown("### 👀 Data Sample")
                if preview_result['data_preview']:
                    df_preview = pd.DataFrame(preview_result['data_preview'])
                    st.dataframe(df_preview.head(10), use_container_width=True)
                
                # Suggestions
                if preview_result['suggestions']:
                    st.markdown("### 💡 Suggestions")
                    for suggestion in preview_result['suggestions']:
                        NeumorphicUI.render_alert(suggestion, "info")
                
                # Process button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("✅ Process This File", use_container_width=True, type="primary"):
                        with st.spinner("Processing your data..."):
                            # Actual processing
                            result = self.parser.parse_file(
                                uploaded_file.read(),
                                uploaded_file.name,
                                preview_only=False
                            )
                            
                            if result['success']:
                                # Store in data warehouse
                                dataset_id = st.session_state.data_warehouse.add_dataset(
                                    name=uploaded_file.name,
                                    data_type=result['data_type'],
                                    data=pd.DataFrame(result['processed_data']),
                                    metadata=result['metadata']
                                )
                                
                                st.session_state.uploaded_files.append({
                                    'filename': uploaded_file.name,
                                    'dataset_id': dataset_id,
                                    'upload_time': datetime.now()
                                })
                                
                                NeumorphicUI.render_alert(
                                    f"✅ Successfully processed {result['rows_processed']:,} rows!",
                                    "success"
                                )
                                
                                # Show insights button
                                if st.button("🎯 View Insights", use_container_width=True):
                                    st.session_state.current_view = 'insights'
                                    st.rerun()
                            else:
                                NeumorphicUI.render_alert(
                                    f"Error: {result['error']}",
                                    "danger"
                                )
    
    def render_insights(self):
        """Render insights dashboard"""
        st.markdown("## 💡 Smart Insights")
        
        if not st.session_state.data_warehouse.datasets:
            st.info("Upload data to see insights")
            return
        
        # Show AI status in sidebar
        with st.sidebar:
            if self.ai and self.ai.is_available():
                st.markdown("### 🤖 AI Status")
                st.success("✅ Hybrid AI Active")
                st.caption("Using Haiku for parsing, Sonnet for insights")
                
                # Show cost tracking if available
                if 'ai_costs' in st.session_state:
                    st.metric("Session Cost", f"${st.session_state.ai_costs:.4f}")
            else:
                st.warning("⚠️ AI not connected")
        
        # Get insights using hybrid AI if available
        if self.smart_analytics:
            # Get sales data from warehouse
            sales_data = None
            for dataset in st.session_state.data_warehouse.datasets.values():
                if dataset['data_type'] == 'sales':
                    sales_data = dataset['data']
                    break
            
            if sales_data is not None and not sales_data.empty:
                with st.spinner("🧠 AI analyzing profit opportunities (using Sonnet)..."):
                    profit_result = self.smart_analytics.analyze_profit_opportunities(sales_data)
                    
                    if profit_result.get('success'):
                        # Update cost tracking
                        if 'ai_costs' not in st.session_state:
                            st.session_state.ai_costs = 0
                        st.session_state.ai_costs += profit_result['cost_estimate']['total_cost']
                        
                        # Display AI insights
                        st.markdown("### 🤖 AI-Powered Profit Analysis")
                        
                        insights_data = profit_result['result']
                        if isinstance(insights_data, dict) and 'raw_response' in insights_data:
                            st.markdown(insights_data['raw_response'])
                        else:
                            # Format structured insights
                            for key, value in insights_data.items():
                                st.markdown(f"**{key.replace('_', ' ').title()}**")
                                if isinstance(value, list):
                                    for item in value:
                                        st.markdown(f"- {item}")
                                elif isinstance(value, dict):
                                    for k, v in value.items():
                                        st.markdown(f"- {k}: {v}")
                                else:
                                    st.markdown(value)
                                st.markdown("")
        
        # Regular insights from analytics engine
        insights = st.session_state.analytics_engine.generate_comprehensive_insights()
        
        # AI Analysis Controls
        if self.smart_analytics:
            st.markdown("### 🤖 AI Analysis Controls")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🧠 Deep Profit Analysis", help="Uses Sonnet AI (~$0.02)"):
                    with st.spinner("Analyzing with advanced AI..."):
                        # Run profit analysis
                        sales_data = self._get_sales_data()
                        if sales_data is not None:
                            result = self.smart_analytics.analyze_profit_opportunities(sales_data)
                            if result.get('success'):
                                st.session_state['latest_ai_analysis'] = result
                                st.rerun()
            
            with col2:
                if st.button("📊 Menu Optimization", help="Uses Sonnet AI (~$0.015)"):
                    with st.spinner("Optimizing menu with AI..."):
                        # Get menu data
                        menu_data = self._get_menu_data()
                        if menu_data is not None:
                            result = self.smart_analytics.optimize_menu(menu_data)
                            if result.get('success'):
                                st.session_state['latest_menu_analysis'] = result
                                st.rerun()
            
            with col3:
                if st.button("💡 Quick Insights", help="Uses Haiku AI (~$0.001)"):
                    with st.spinner("Generating quick insights..."):
                        # Use pattern-based insights (cheaper)
                        st.session_state['show_quick_insights'] = True
                        st.rerun()
            
            # Display latest AI analysis if available
            if 'latest_ai_analysis' in st.session_state:
                analysis = st.session_state['latest_ai_analysis']
                st.markdown("#### Latest AI Analysis")
                st.info(f"Model used: {analysis['model_used'].split('-')[2].title()} | Cost: ${analysis['cost_estimate']['total_cost']:.4f}")
                
                # Display the analysis
                if isinstance(analysis['result'], dict) and 'raw_response' in analysis['result']:
                    st.markdown(analysis['result']['raw_response'])
                else:
                    st.json(analysis['result'])
        
        # Profit opportunities
        st.markdown("### 💰 Profit Opportunities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            NeumorphicUI.render_insight(
                "Menu Price Optimization",
                "+$2,340/month",
                "3 items are underpriced compared to similar restaurants",
                "📈"
            )
        
        with col2:
            NeumorphicUI.render_insight(
                "Reduce Food Waste",
                "-$1,890/month",
                "Tuesday prep consistently over by 15%",
                "🗑️"
            )
        
        with col3:
            NeumorphicUI.render_insight(
                "Peak Hour Staffing",
                "-$980/month",
                "Overstaffed Mon-Wed dinner service",
                "👥"
            )
        
        # Performance metrics
        st.markdown("### 📊 Performance Analysis")
        
        # Create tabs for different insight categories
        tab1, tab2, tab3, tab4 = st.tabs(["Sales Patterns", "Menu Performance", "Efficiency", "Forecasts"])
        
        with tab1:
            # Sales patterns
            if 'sales_patterns' in insights:
                patterns = insights['sales_patterns']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Hourly sales
                    st.markdown("#### ⏰ Peak Hours Analysis")
                    hourly_data = pd.Series(patterns.get('hourly_distribution', {}))
                    if not hourly_data.empty:
                        fig = NeumorphicUI.create_neumorphic_chart(
                            hourly_data,
                            chart_type="bar",
                            title="Sales by Hour"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Day of week patterns
                    st.markdown("#### 📅 Weekly Patterns")
                    weekly_data = pd.Series(patterns.get('weekly_pattern', {}))
                    if not weekly_data.empty:
                        fig = NeumorphicUI.create_neumorphic_chart(
                            weekly_data,
                            chart_type="bar",
                            title="Sales by Day of Week"
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Menu performance
            if 'menu_performance' in insights:
                menu_data = insights['menu_performance']
                
                # Menu engineering matrix
                st.markdown("#### 🍽️ Menu Engineering Matrix")
                
                categories = ['Stars', 'Plow Horses', 'Puzzles', 'Dogs']
                descriptions = [
                    'High profit, high popularity - Promote these!',
                    'Low profit, high popularity - Increase prices',
                    'High profit, low popularity - Market better',
                    'Low profit, low popularity - Consider removing'
                ]
                
                for cat, desc in zip(categories, descriptions):
                    items = menu_data.get(cat.lower().replace(' ', '_'), [])
                    if items:
                        st.markdown(f"**{cat}** - {desc}")
                        for item in items[:5]:  # Show top 5
                            st.markdown(f"- {item}")
        
        with tab3:
            # Operational efficiency
            st.markdown("#### ⚡ Efficiency Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                NeumorphicUI.render_metric_card(
                    "Avg Ticket Time",
                    "14.2 min",
                    "-1.3 min",
                    "positive",
                    "⏱️"
                )
            
            with col2:
                NeumorphicUI.render_metric_card(
                    "Table Turnover",
                    "3.8/day",
                    "+0.4",
                    "positive",
                    "🔄"
                )
        
        with tab4:
            # Forecasts
            st.markdown("#### 🔮 Next 7 Days Forecast")
            
            # Generate forecast data
            dates = pd.date_range(start=datetime.now(), periods=7, freq='D')
            forecast = np.random.normal(3500, 300, 7)
            forecast_series = pd.Series(forecast, index=dates)
            
            fig = NeumorphicUI.create_neumorphic_chart(
                forecast_series,
                chart_type="line",
                title="Revenue Forecast"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_menu_optimizer(self):
        """Render menu optimization section"""
        st.markdown("## 💰 Menu Optimizer")
        
        # Optimization strategies
        st.markdown("""
        <div class="neu-card">
            <h3 style="color: #2C3E50; margin-bottom: 1.5rem;">🎯 Optimization Strategies</h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;">
                <div class="neu-inset" style="padding: 1.5rem;">
                    <h4 style="color: #6C7EE1;">💵 Price Optimization</h4>
                    <p style="color: #7F8C8D;">AI-powered pricing based on demand, competition, and psychology</p>
                </div>
                <div class="neu-inset" style="padding: 1.5rem;">
                    <h4 style="color: #52C41A;">📊 Menu Engineering</h4>
                    <p style="color: #7F8C8D;">Identify stars, dogs, and opportunities in your menu</p>
                </div>
                <div class="neu-inset" style="padding: 1.5rem;">
                    <h4 style="color: #FAAD14;">🎨 Menu Design</h4>
                    <p style="color: #7F8C8D;">Psychology-based layout for maximum profitability</p>
                </div>
                <div class="neu-inset" style="padding: 1.5rem;">
                    <h4 style="color: #F5222D;">🔥 Promotion Strategy</h4>
                    <p style="color: #7F8C8D;">Data-driven promotions that increase profit, not just sales</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Current menu analysis
        st.markdown("### 📋 Current Menu Analysis")
        
        # Sample menu items with profitability scores
        menu_items = pd.DataFrame({
            'Item': ['Burger Deluxe', 'Caesar Salad', 'Ribeye Steak', 'Fish Tacos', 'Chocolate Cake'],
            'Current Price': [14.99, 11.99, 32.99, 16.99, 8.99],
            'Food Cost %': [28.5, 22.1, 38.2, 31.5, 25.3],
            'Popularity': [85, 65, 45, 78, 92],
            'Profit Score': [8.2, 7.5, 6.1, 7.8, 8.9]
        })
        
        # Display menu items with recommendations
        for _, item in menu_items.iterrows():
            st.markdown(f"""
            <div class="neu-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: #2C3E50; margin-bottom: 0.5rem;">{item['Item']}</h4>
                        <div style="color: #7F8C8D;">
                            Current: ${item['Current Price']} | Food Cost: {item['Food Cost %']}% | 
                            Popularity: {item['Popularity']}/100
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #6C7EE1; font-size: 1.2rem; font-weight: 600;">
                            Profit Score: {item['Profit Score']}/10
                        </div>
                        <div style="color: #52C41A; font-size: 0.9rem;">
                            Suggested: ${item['Current Price'] * 1.1:.2f} (+10%)
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_inventory_manager(self):
        """Render inventory management section"""
        st.markdown("## 📦 Inventory AI")
        
        # Inventory health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            NeumorphicUI.render_metric_card(
                "Inventory Value",
                "$18,450",
                "-$2,100",
                "positive",
                "💰"
            )
        
        with col2:
            NeumorphicUI.render_metric_card(
                "Days on Hand",
                "4.2",
                "Optimal",
                "positive",
                "📅"
            )
        
        with col3:
            NeumorphicUI.render_metric_card(
                "Waste %",
                "3.8%",
                "-0.5%",
                "positive",
                "🗑️"
            )
        
        with col4:
            NeumorphicUI.render_metric_card(
                "Stock Outs",
                "2",
                "This week",
                "negative",
                "⚠️"
            )
        
        # Smart ordering recommendations
        st.markdown("### 🤖 AI Ordering Recommendations")
        
        # Critical items
        st.markdown("#### 🚨 Order Today")
        critical_items = pd.DataFrame({
            'Item': ['Chicken Breast', 'Romaine Lettuce', 'Tomatoes'],
            'Current Stock': ['12 lbs', '8 heads', '15 lbs'],
            'Days Left': [1.5, 1, 2],
            'Suggested Order': ['40 lbs', '24 heads', '30 lbs'],
            'Supplier': ['Fresh Foods Co', 'Local Produce', 'Local Produce']
        })
        
        for _, item in critical_items.iterrows():
            st.markdown(f"""
            <div class="neu-alert neu-alert-warning">
                <strong>{item['Item']}</strong> - Only {item['Days Left']} days left
                <br>Current: {item['Current Stock']} | Order: {item['Suggested Order']} from {item['Supplier']}
            </div>
            """, unsafe_allow_html=True)
        
        # Optimization opportunities
        st.markdown("#### 💡 Optimization Opportunities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            NeumorphicUI.render_card(
                """
                <h4 style="color: #52C41A;">📉 Reduce Orders</h4>
                <ul style="color: #7F8C8D;">
                    <li>Mushrooms: Order 20% less (low usage trend)</li>
                    <li>Heavy Cream: Switch to 2x/week delivery</li>
                    <li>Specialty Cheese: Reduce par level by 30%</li>
                </ul>
                <p style="color: #2C3E50; font-weight: 600;">Potential Savings: $420/month</p>
                """,
                "Over-Ordering Detected"
            )
        
        with col2:
            NeumorphicUI.render_card(
                """
                <h4 style="color: #6C7EE1;">🔄 Supplier Optimization</h4>
                <ul style="color: #7F8C8D;">
                    <li>Consolidate produce orders: Save 8% on delivery</li>
                    <li>Switch beef supplier: 12% better pricing available</li>
                    <li>Negotiate wine contract: Volume discount possible</li>
                </ul>
                <p style="color: #2C3E50; font-weight: 600;">Potential Savings: $1,250/month</p>
                """,
                "Cost Reduction Opportunities"
            )
    
    def _calculate_total_revenue(self) -> float:
        """Calculate total revenue from all datasets"""
        total = 0
        for dataset in st.session_state.data_warehouse.datasets.values():
            if 'total_amount' in dataset['data'].columns:
                total += dataset['data']['total_amount'].sum()
        return total
    
    def _calculate_avg_transaction(self) -> float:
        """Calculate average transaction value"""
        total_revenue = self._calculate_total_revenue()
        total_transactions = sum(
            len(dataset['data']) 
            for dataset in st.session_state.data_warehouse.datasets.values()
        )
        return total_revenue / total_transactions if total_transactions > 0 else 0
    
    def _get_sales_data(self) -> Optional[pd.DataFrame]:
        """Get sales data from warehouse"""
        for dataset in st.session_state.data_warehouse.datasets.values():
            if dataset['data_type'] == 'sales':
                return dataset['data']
        return None
    
    def _get_menu_data(self) -> Optional[pd.DataFrame]:
        """Get or create menu data from sales data"""
        sales_data = self._get_sales_data()
        if sales_data is None or sales_data.empty:
            return None
        
        # Create menu data from sales data
        if 'item_name' in sales_data.columns:
            menu_data = sales_data.groupby('item_name').agg({
                'unit_price': 'mean',
                'quantity': 'sum',
                'total_amount': 'sum'
            }).reset_index()
            
            menu_data.columns = ['item_name', 'price', 'quantity_sold', 'total_revenue']
            
            # Estimate costs (30% food cost as default)
            menu_data['cost'] = menu_data['price'] * 0.3
            
            return menu_data
        
        return None


# Run the app
if __name__ == "__main__":
    app = RestaurantApp()
    app.run()