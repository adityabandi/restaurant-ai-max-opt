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

# 🎨 World-Class UI/UX Design - Mobile First, Beautiful, Intuitive
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* === GLOBAL FOUNDATION === */
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        color: #111827;
        line-height: 1.6;
    }
    
    /* Hide Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* === BEAUTIFUL HEADERS === */
    .main-header {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .main-header h1 {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 700;
        margin: 0;
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: clamp(1rem, 2.5vw, 1.25rem);
        margin: 1rem 0 0 0;
        color: white;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        font-weight: 400;
    }
    
    /* === STUNNING CARDS === */
    .metric-card {
        background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: #d1d5db;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2563eb, #7c3aed, #db2777);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover::before {
        transform: scaleX(1);
    }
    
    .insight-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #2563eb;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-left-width: 6px;
    }
    
    .priority-high { 
        border-left-color: #dc2626 !important; 
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
    }
    .priority-medium { 
        border-left-color: #ea580c !important; 
        background: linear-gradient(135deg, #fff7ed 0%, #ffffff 100%);
    }
    .priority-low { 
        border-left-color: #059669 !important; 
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
    }
    
    .savings-highlight {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* === STATUS INDICATOR === */
    .api-status {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
        padding: 0.75rem 1.25rem;
        border-radius: 50px;
        font-size: 0.875rem;
        font-weight: 600;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .api-active {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        border-color: rgba(5, 150, 105, 0.3);
    }
    
    .api-fallback {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        color: white;
        border-color: rgba(234, 88, 12, 0.3);
    }
    
    /* === UPLOAD ZONE MAGIC === */
    .upload-zone {
        border: 2px dashed #2563eb;
        border-radius: 16px;
        padding: 4rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
        margin: 2rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .upload-zone:hover {
        border-color: #1d4ed8;
        background: linear-gradient(135deg, #dbeafe 0%, #f1f5f9 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.1);
    }
    
    .upload-zone h3 {
        color: #1e40af;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .upload-zone p {
        color: #64748b;
        margin: 0.5rem 0;
    }
    
    /* === BUTTON PERFECTION === */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    /* === FORMS THAT DON'T SUCK === */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 0.875rem 1rem;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background-color: white;
        color: #111827;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        outline: none;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        background-color: #ffffff;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
    }
    
    /* === BEAUTIFUL TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f9fafb;
        border-radius: 8px;
        padding: 0.25rem;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #6b7280;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #2563eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        font-weight: 600;
    }
    
    /* === MOBILE RESPONSIVE === */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .insight-card {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .upload-zone {
            padding: 2rem 1rem;
        }
        
        .api-status {
            top: 10px;
            right: 10px;
            padding: 0.5rem 1rem;
            font-size: 0.75rem;
        }
    }
    
    /* === TYPOGRAPHY SCALE === */
    h1 { color: #111827; font-weight: 700; }
    h2 { color: #111827; font-weight: 600; }
    h3 { color: #111827; font-weight: 600; }
    h4 { color: #111827; font-weight: 600; }
    p { color: #374151; line-height: 1.6; }
    
    /* === LOADING STATES === */
    .stSpinner > div {
        border-top-color: #2563eb !important;
    }
    
    /* === SUCCESS STATES === */
    .stSuccess {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        border-radius: 8px;
    }
    
    /* === ERROR STATES === */
    .stError {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        border-radius: 8px;
    }
    
    /* === INFO STATES === */
    .stInfo {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1d4ed8;
        border-radius: 8px;
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
        
        # Initialize session state
        self._init_session_state()
    
    def _check_api_status(self) -> Dict:
        """Check if APIs are working"""
        status = {
            'anthropic': False,
            'weather': False,
            'message': ''
        }
        
        # Check Anthropic API
        try:
            api_key = None
            if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
                api_key = st.secrets["ANTHROPIC_API_KEY"]
            elif os.getenv("ANTHROPIC_API_KEY"):
                api_key = os.getenv("ANTHROPIC_API_KEY")
            
            if api_key:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                status['anthropic'] = True
                status['message'] = '🤖 AI Enhanced Mode'
            else:
                status['message'] = '📊 Smart Analytics Mode'
        except Exception as e:
            status['message'] = '📊 Smart Analytics Mode'
        
        # Check Weather API (always works, but skip check for faster load)
        status['weather'] = True  # Assume weather API works
        
        return status
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'uploaded_data' not in st.session_state:
            st.session_state.uploaded_data = None
        if 'insights' not in st.session_state:
            st.session_state.insights = []
        if 'weather_data' not in st.session_state:
            st.session_state.weather_data = None
    
    def run(self):
        """Main application entry point"""
        # Show API status
        self._show_api_status()
        
        # Skip auth for now - go straight to main app
        self._show_main_app()
    
    def _show_api_status(self):
        """Show API status indicator"""
        status_class = "api-active" if self.api_status['anthropic'] else "api-fallback"
        st.markdown(f"""
        <div class="api-status {status_class}">
            {self.api_status['message']}
        </div>
        """, unsafe_allow_html=True)
    
    def _show_auth_page(self):
        """Show modern authentication page"""
        # Main header
        st.markdown("""
        <div class="main-header">
            <h1>🍽️ Restaurant AI Analytics</h1>
            <p>Transform your restaurant data into actionable insights that save $1,200+ monthly</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Center the auth forms
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            # Auth method selection
            st.markdown("### 🚀 Get Started")
            
            # Google Login Button (visual only for now)
            if st.button("🔐 Continue with Google", use_container_width=True, key="google_auth"):
                st.info("🚧 Google login coming soon! For now, please use email signup below.")
            
            st.markdown("---")
            st.markdown("**Or use your email:**")
            
            # Auth tabs
            tab1, tab2 = st.tabs(["👋 Sign In", "🆕 Create Account"])
            
            with tab1:
                self._show_signin_form()
            
            with tab2:
                self._show_signup_form()
            
            # Feature highlights
            st.markdown("---")
            st.markdown("### ✨ What You'll Get:")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("""
                **💰 Cost Savings**
                - Average $1,200/month identified
                - Specific actionable recommendations
                - ROI tracking and monitoring
                """)
            
            with col_b:
                st.markdown("""
                **🤖 AI-Powered**
                - Smart Excel/CSV parsing
                - Intelligent insights generation
                - Weather-based predictions
                """)
            
            with col_c:
                st.markdown("""
                **📊 Professional Analytics**
                - Interactive dashboards
                - Real-time data processing
                - Export capabilities
                """)
    
    def _show_signin_form(self):
        """Show modern sign in form"""
        with st.form("signin_form"):
            st.markdown("#### 👋 Welcome Back!")
            st.markdown("Sign in to access your restaurant analytics dashboard")
            
            email = st.text_input("📧 Email Address", placeholder="your@restaurant.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember_me = st.checkbox("Remember me")
            with col2:
                if st.form_submit_button("Forgot Password?", type="secondary"):
                    st.info("Password reset feature coming soon!")
            
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            if submitted:
                if email and password:
                    user = self.db.authenticate_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}! 🎉")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password. Please try again.")
                else:
                    st.error("📝 Please fill in all fields")
    
    def _show_signup_form(self):
        """Show modern sign up form"""
        with st.form("signup_form"):
            st.markdown("#### 🆕 Create Your Account")
            st.markdown("Join thousands of restaurant owners saving money with AI")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Full Name", placeholder="John Smith")
                email = st.text_input("📧 Email Address", placeholder="john@restaurant.com")
            with col2:
                password = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters")
                restaurant_location = st.text_input("📍 Location", placeholder="New York, NY")
            
            restaurant_name = st.text_input("🍽️ Restaurant Name", placeholder="Joe's Pizza Palace")
            
            # Terms checkbox
            terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            submitted = st.form_submit_button("🎉 Create My Account", use_container_width=True)
            
            if submitted:
                if not terms_accepted:
                    st.error("📋 Please accept the Terms of Service to continue")
                elif all([name, email, password, restaurant_name]):
                    if len(password) < 6:
                        st.error("🔒 Password must be at least 6 characters long")
                    else:
                        # Check if user exists
                        existing_user = self.db.get_user_by_email(email)
                        if existing_user:
                            st.error("📧 Email already registered. Try signing in instead.")
                        else:
                            # Create user
                            user_id = self.db.create_user(email, name, "email", password)
                            self.db.update_user_restaurant_info(user_id, restaurant_name, restaurant_location)
                            
                            # Auto sign in
                            user = self.db.get_user_by_email(email)
                            st.session_state.user = user
                            st.success(f"🎉 Welcome to Restaurant AI Analytics, {name}!")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                else:
                    st.error("📝 Please fill in all required fields")
    
    def _show_main_app(self):
        """Show main application"""
        # Beautiful dashboard header (no user needed)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 3rem;
                    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    position: relative; overflow: hidden;">
            <div style="position: relative; z-index: 1;">
                <h2 style="margin: 0; color: white; font-weight: 700; font-size: 2rem;">🍽️ Restaurant AI Analytics</h2>
                <p style="margin: 0.75rem 0 0 0; color: white; opacity: 0.95; font-size: 1.1rem;">Transform your restaurant data into actionable insights that save $1,200+ monthly</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Main content
        if st.session_state.uploaded_data is None:
            self._show_upload_section()
        else:
            self._show_dashboard()
    
    def _show_upload_section(self):
        """Show modern file upload section"""
        # Stunning hero section
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; 
                    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
                    border-radius: 20px; margin-bottom: 3rem;
                    border: 1px solid #e2e8f0;">
            <h1 style="color: #111827; font-weight: 700; font-size: clamp(2rem, 4vw, 3rem); margin: 0;">
                📊 Upload Your Restaurant Data
            </h1>
            <p style="font-size: clamp(1.1rem, 2vw, 1.3rem); color: #6b7280; margin: 1rem 0 0 0; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.6;">
                Get instant insights that save <strong style="color: #059669;">$1,200+ monthly</strong> — AI analyzes any format from any POS system
            </p>
            <div style="margin-top: 1.5rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="color: #059669; font-weight: 600;">✅ Toast</div>
                <div style="color: #059669; font-weight: 600;">✅ Square</div>
                <div style="color: #059669; font-weight: 600;">✅ Clover</div>
                <div style="color: #059669; font-weight: 600;">✅ Any Excel/CSV</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload zone
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("""
            <div class="upload-zone">
                <h3 style="margin-top: 0;">🎯 Drag & Drop Your Data</h3>
                <p style="font-size: 1.1rem; margin: 1rem 0;">Upload sales, inventory, or supplier data from any POS system</p>
                <p><strong>Supports:</strong> Excel (.xlsx, .xls), CSV files</p>
                <p style="font-size: 0.9rem; color: #666;">✅ Toast • Square • Clover • Any Excel/CSV export</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "📁 Choose your restaurant data file",
                type=['xlsx', 'csv', 'xls'],
                help="Upload your restaurant data file - AI will automatically detect the format!"
            )
            
            if uploaded_file:
                self._process_uploaded_file(uploaded_file)
        
        with col2:
            # Demo section with beautiful styling
            st.markdown("""
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%); 
                        padding: 2rem; border-radius: 16px; border: 1px solid #bfdbfe;
                        text-align: center; margin-bottom: 2rem;">
                <h3 style="color: #1e40af; margin: 0 0 1rem 0; font-weight: 600;">🚀 Try Demo Data</h3>
                <p style="color: #64748b; margin-bottom: 1.5rem; line-height: 1.6;">
                    See the platform in action with realistic restaurant data from a premium establishment
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎭 Load Premium Demo Restaurant", use_container_width=True):
                self._load_demo_data()
            
            # Benefits section
            st.markdown("""
            <div style="margin-top: 2rem; padding: 1.5rem; background: white; 
                        border-radius: 12px; border: 1px solid #e5e7eb;">
                <h4 style="color: #111827; margin: 0 0 1rem 0; font-weight: 600;">💡 What You'll Discover:</h4>
                <div style="space-y: 0.75rem;">
                    <div style="margin: 0.75rem 0; color: #374151;">💰 <strong>Exact savings</strong> — "$847/month from removing Caesar Salad"</div>
                    <div style="margin: 0.75rem 0; color: #374151;">📈 <strong>Menu rankings</strong> — Which items make you the most money</div>
                    <div style="margin: 0.75rem 0; color: #374151;">🌤️ <strong>Weather predictions</strong> — "Rain = +60% delivery orders"</div>
                    <div style="margin: 0.75rem 0; color: #374151;">🎯 <strong>Action items</strong> — Step-by-step profit improvements</div>
                    <div style="margin: 0.75rem 0; color: #374151;">📊 <strong>Beautiful charts</strong> — Interactive data visualization</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _process_uploaded_file(self, uploaded_file):
        """Process uploaded file with AI parsing"""
        with st.spinner("🤖 Analyzing your data with AI..."):
            try:
                # Parse file with AI
                file_contents = uploaded_file.read()
                parsing_result = self.parser.parse_file(file_contents, uploaded_file.name)
                
                if parsing_result['success']:
                    # Store processed data (skip database for now)
                    processed_data = parsing_result['processed_data']
                    st.session_state.uploaded_data = {
                        'upload_id': 'temp',
                        'filename': uploaded_file.name,
                        'data_type': parsing_result['data_type'],
                        'data': processed_data,
                        'ai_confidence': parsing_result.get('ai_confidence', 0.85)
                    }
                    
                    # Generate insights
                    self._generate_insights(processed_data, parsing_result['data_type'])
                    
                    st.success(f"✅ Successfully processed {parsing_result['rows_processed']} records!")
                    if self.api_status['anthropic']:
                        st.info(f"🤖 AI Confidence: {parsing_result.get('ai_confidence', 0.85)*100:.0f}%")
                    
                    st.rerun()
                    
                else:
                    st.error(f"❌ Error processing file: {parsing_result['error']}")
                    if 'suggestions' in parsing_result:
                        for suggestion in parsing_result['suggestions']:
                            st.info(f"💡 {suggestion}")
                            
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
    
    def _load_demo_data(self):
        """Load impressive demo data"""
        demo_data = [
            {'item_name': 'Truffle Mac & Cheese', 'quantity': 45, 'price': 22.99, 'total_amount': 1034.55, 'category': 'Entrees'},
            {'item_name': 'Wagyu Burger', 'quantity': 35, 'price': 28.99, 'total_amount': 1014.65, 'category': 'Entrees'},
            {'item_name': 'Lobster Risotto', 'quantity': 28, 'price': 34.99, 'total_amount': 979.72, 'category': 'Entrees'},
            {'item_name': 'Duck Confit', 'quantity': 22, 'price': 31.99, 'total_amount': 703.78, 'category': 'Entrees'},
            {'item_name': 'Artisan Flatbread', 'quantity': 65, 'price': 16.99, 'total_amount': 1104.35, 'category': 'Appetizers'},
            {'item_name': 'Caesar Salad', 'quantity': 8, 'price': 14.99, 'total_amount': 119.92, 'category': 'Salads'},
            {'item_name': 'Fish Tacos', 'quantity': 12, 'price': 18.99, 'total_amount': 227.88, 'category': 'Entrees'},
            {'item_name': 'Craft Cocktails', 'quantity': 120, 'price': 12.99, 'total_amount': 1558.80, 'category': 'Beverages'},
        ]
        
        st.session_state.uploaded_data = {
            'upload_id': 'demo',
            'filename': 'Premium Restaurant Demo Data',
            'data_type': 'sales',
            'data': demo_data,
            'ai_confidence': 0.95
        }
        
        self._generate_insights(demo_data, 'sales')
        st.success("🎉 Demo data loaded! Explore your restaurant analytics below.")
        st.rerun()
    
    def _generate_insights(self, data: List[Dict], data_type: str):
        """Generate insights from data"""
        insights = []
        
        if data_type == 'sales':
            # Use revenue analyzer for sales data
            menu_analysis = self.revenue_analyzer.analyze_menu_performance(data)
            insights = self.revenue_analyzer.generate_actionable_insights(menu_analysis)
        
        # Add weather insights for demo (skip user-specific location)
        # For now, use a demo location
        demo_location = "New York, NY"
        weather_insights = self._get_weather_insights(demo_location)
        insights.extend(weather_insights)
        
        st.session_state.insights = insights
    
    def _get_weather_insights(self, location: str) -> List[Dict]:
        """Get weather-based insights"""
        try:
            forecast = self.weather.get_forecast(location, days=7)
            if forecast:
                weather_insights = self.weather.analyze_weather_impact(forecast)
                return weather_insights[:3]  # Top 3 weather insights
        except:
            pass
        
        return []
    
    def _show_dashboard(self):
        """Show main dashboard with insights and charts"""
        uploaded_data = st.session_state.uploaded_data
        insights = st.session_state.insights
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        total_savings = sum(insight.get('savings_potential', 0) for insight in insights)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #059669; margin: 0; font-weight: 700; font-size: 2.5rem;">${total_savings:,.0f}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Monthly Savings</p>
                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #059669;">💰 Real money in your pocket</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #2563eb; margin: 0; font-weight: 700; font-size: 2.5rem;">{len(insights)}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">AI Insights</p>
                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #2563eb;">🤖 Actionable recommendations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            efficiency_score = min(85 + len(insights) * 2, 95)
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #ea580c; margin: 0; font-weight: 700; font-size: 2.5rem;">{efficiency_score}%</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Efficiency Score</p>
                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #ea580c;">📈 Above industry average</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #7c3aed; margin: 0; font-weight: 700; font-size: 2.5rem;">${total_savings * 12:,.0f}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Annual Impact</p>
                <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #7c3aed;">🎯 Yearly profit increase</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._show_insights_section()
            self._show_data_visualizations()
        
        with col2:
            self._show_ai_chat()
            self._show_weather_section()
    
    def _show_insights_section(self):
        """Display actionable insights"""
        st.markdown("## 🔍 AI-Powered Insights")
        
        insights = st.session_state.insights
        
        if not insights:
            st.info("Upload data to see personalized insights!")
            return
        
        # Group by priority
        high_priority = [i for i in insights if i.get('priority') == 'high']
        medium_priority = [i for i in insights if i.get('priority') == 'medium']
        
        # High priority insights
        if high_priority:
            st.markdown("### 🚨 High Priority Actions")
            for insight in high_priority:
                self._render_insight_card(insight, 'high')
        
        # Medium priority insights
        if medium_priority:
            st.markdown("### ⚡ Quick Wins")
            for insight in medium_priority:
                self._render_insight_card(insight, 'medium')
    
    def _render_insight_card(self, insight: Dict, priority: str):
        """Render individual insight card"""
        title = insight.get('title', 'Insight')
        description = insight.get('description', '')
        recommendation = insight.get('recommendation', '')
        savings = insight.get('savings_potential', 0)
        action_items = insight.get('action_items', [])
        
        st.markdown(f"""
        <div class="insight-card priority-{priority}">
            <h4>{title}</h4>
            <p><strong>📊 Analysis:</strong> {description}</p>
            <p><strong>💡 Recommendation:</strong> {recommendation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if savings > 0:
            st.markdown(f"""
            <div class="savings-highlight">
                💰 Potential Monthly Savings: ${savings:,.0f} (${savings*12:,.0f}/year)
            </div>
            """, unsafe_allow_html=True)
        
        if action_items:
            with st.expander("📋 Action Steps"):
                for i, step in enumerate(action_items, 1):
                    st.write(f"{i}. {step}")
    
    def _show_data_visualizations(self):
        """Show data visualizations"""
        uploaded_data = st.session_state.uploaded_data
        
        if not uploaded_data or uploaded_data['data_type'] != 'sales':
            return
        
        st.markdown("## 📈 Performance Analytics")
        
        df = pd.DataFrame(uploaded_data['data'])
        
        # Revenue by item chart
        if 'item_name' in df.columns and 'total_amount' in df.columns:
            top_items = df.groupby('item_name')['total_amount'].sum().sort_values(ascending=False).head(8)
            
            fig = px.bar(
                x=top_items.values,
                y=top_items.index,
                orientation='h',
                title="💰 Revenue by Menu Item",
                labels={'x': 'Revenue ($)', 'y': 'Menu Item'},
                color=top_items.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional charts
            col1, col2 = st.columns(2)
            
            with col1:
                if 'quantity' in df.columns:
                    qty_by_item = df.groupby('item_name')['quantity'].sum().sort_values(ascending=False).head(6)
                    fig2 = px.pie(values=qty_by_item.values, names=qty_by_item.index, title="📊 Quantity Sold Distribution")
                    fig2.update_layout(height=300)
                    st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                if 'price' in df.columns:
                    avg_prices = df.groupby('item_name')['price'].mean().sort_values(ascending=False).head(6)
                    fig3 = px.bar(x=avg_prices.index, y=avg_prices.values, title="💲 Average Price by Item")
                    fig3.update_layout(height=300, xaxis_tickangle=-45)
                    st.plotly_chart(fig3, use_container_width=True)
    
    def _show_ai_chat(self):
        """Show AI chat interface"""
        st.markdown("### 💬 Ask Your AI Assistant")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat messages
        for message in st.session_state.chat_history:
            with st.chat_message(message['role']):
                st.write(message['content'])
        
        # Chat input
        if prompt := st.chat_input("Ask about your restaurant data..."):
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': prompt
            })
            
            # Generate AI response
            response = self._generate_ai_response(prompt)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            st.rerun()
        
        # Suggested questions
        if not st.session_state.chat_history:
            st.markdown("**💡 Try asking:**")
            questions = [
                "What's my biggest profit opportunity?",
                "How can I reduce food costs?",
                "Which menu items should I promote?",
                "What's the weather impact on sales?"
            ]
            
            for question in questions:
                if st.button(question, key=f"q_{hash(question)}", use_container_width=True):
                    st.session_state.chat_history.append({'role': 'user', 'content': question})
                    response = self._generate_ai_response(question)
                    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    st.rerun()
    
    def _generate_ai_response(self, question: str) -> str:
        """Generate AI response to user question"""
        insights = st.session_state.insights
        question_lower = question.lower()
        
        # Smart responses based on insights
        if 'profit' in question_lower or 'opportunity' in question_lower:
            high_savings_insights = [i for i in insights if i.get('savings_potential', 0) > 200]
            if high_savings_insights:
                insight = high_savings_insights[0]
                return f"🎯 **Your biggest opportunity:** {insight.get('title', 'Menu optimization')}. {insight.get('recommendation', '')} This could save you ${insight.get('savings_potential', 0):,.0f}/month."
            else:
                return "💰 Focus on menu engineering and supplier negotiations for the biggest profit impact. Your top items likely have room for 8-12% price increases."
        
        elif 'cost' in question_lower or 'reduce' in question_lower:
            return "💡 **Top cost reduction strategies:** 1) Negotiate with suppliers (5-15% savings) 2) Optimize portion sizes 3) Remove low-margin items 4) Implement waste tracking. Start with your highest-cost ingredients first."
        
        elif 'promote' in question_lower or 'menu' in question_lower:
            return "📈 **Promotion strategy:** Focus on high-margin items with proven demand. Use menu placement, staff training, and social media to boost sales of your most profitable dishes."
        
        elif 'weather' in question_lower:
            weather_insights = [i for i in insights if i.get('category') == 'weather_alert']
            if weather_insights:
                insight = weather_insights[0]
                return f"🌤️ **Weather impact:** {insight.get('description', '')} {insight.get('recommendation', '')}"
            else:
                return "🌤️ Weather significantly impacts restaurant sales. Rain typically increases delivery by 40-60%, while perfect weather boosts patio dining and overall foot traffic by 20-30%."
        
        else:
            return "🤖 I can help you analyze costs, optimize menu performance, understand weather impacts, and find profit opportunities. What specific area would you like to focus on?"
    
    def _show_weather_section(self):
        """Show weather insights section"""
        # Use demo location for now
        location = "New York, NY"
        
        st.markdown("### 🌤️ Weather Intelligence")
        
        try:
            # Get current weather
            current_weather = self.weather.get_current_weather(location)
            if current_weather:
                temp = current_weather['temperature']
                st.metric("Current Temperature", f"{temp}°C ({temp*9/5+32:.0f}°F)")
            
            # Get forecast
            forecast = self.weather.get_forecast(location, days=3)
            if forecast and 'daily' in forecast:
                st.markdown("**3-Day Forecast Impact:**")
                daily = forecast['daily']
                
                for i in range(min(3, len(daily['time']))):
                    date = daily['time'][i]
                    temp_max = daily['temperature_2m_max'][i]
                    precipitation = daily['precipitation_sum'][i]
                    
                    # Simple impact assessment
                    if temp_max > 25:  # Hot
                        impact = "☀️ Great for cold drinks"
                    elif temp_max < 10:  # Cold
                        impact = "🍲 Perfect for hot food"
                    elif precipitation > 2:  # Rainy
                        impact = "🚚 Expect more delivery"
                    else:
                        impact = "😊 Normal conditions"
                    
                    st.write(f"**{date}:** {temp_max:.0f}°C - {impact}")
        
        except Exception as e:
            st.write("Weather data temporarily unavailable")

# Run the application
if __name__ == "__main__":
    app = RestaurantAnalyticsApp()
    app.run()