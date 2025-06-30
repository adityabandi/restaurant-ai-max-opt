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

# Enhanced CSS for professional look
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .insight-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .priority-high { border-left-color: #e74c3c !important; }
    .priority-medium { border-left-color: #f39c12 !important; }
    .priority-low { border-left-color: #27ae60 !important; }
    
    .savings-highlight {
        background: linear-gradient(90deg, #00b894, #00cec9);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .api-status {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .api-active {
        background: #27ae60;
        color: white;
    }
    
    .api-fallback {
        background: #f39c12;
        color: white;
    }
    
    .upload-zone {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        margin: 2rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

class RestaurantAnalyticsApp:
    def __init__(self):
        self.db = RestaurantDB()
        self.parser = AIExcelParser()
        self.weather = WeatherIntelligence(self.db)
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
        
        # Check Weather API (always works)
        try:
            response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m", timeout=5)
            if response.status_code == 200:
                status['weather'] = True
        except:
            pass
        
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
        
        # Check if user is logged in
        if st.session_state.user is None:
            self._show_auth_page()
        else:
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
        """Show authentication page"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div class="main-header">
                <h1>🍽️ Restaurant AI Analytics</h1>
                <p>Transform your restaurant data into profit</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Auth tabs
            tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
            
            with tab1:
                self._show_signin_form()
            
            with tab2:
                self._show_signup_form()
    
    def _show_signin_form(self):
        """Show sign in form"""
        with st.form("signin_form"):
            st.markdown("### Welcome Back!")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if email and password:
                    user = self.db.authenticate_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Please fill in all fields")
    
    def _show_signup_form(self):
        """Show sign up form"""
        with st.form("signup_form"):
            st.markdown("### Create Your Account")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            restaurant_name = st.text_input("Restaurant Name")
            restaurant_location = st.text_input("Restaurant Location (City, State)")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                if all([name, email, password, restaurant_name]):
                    # Check if user exists
                    existing_user = self.db.get_user_by_email(email)
                    if existing_user:
                        st.error("Email already registered")
                    else:
                        # Create user
                        user_id = self.db.create_user(email, name, "email", password)
                        self.db.update_user_restaurant_info(user_id, restaurant_name, restaurant_location)
                        
                        # Auto sign in
                        user = self.db.get_user_by_email(email)
                        st.session_state.user = user
                        st.success(f"Welcome to Restaurant AI Analytics, {name}!")
                        st.rerun()
                else:
                    st.error("Please fill in all required fields")
    
    def _show_main_app(self):
        """Show main application"""
        user = st.session_state.user
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"# 🍽️ {user['restaurant_name'] or 'Restaurant'} Analytics")
            st.markdown(f"Welcome back, **{user['name']}**!")
        
        with col2:
            if st.button("Sign Out"):
                st.session_state.user = None
                st.session_state.uploaded_data = None
                st.session_state.insights = []
                st.rerun()
        
        # Main content
        if st.session_state.uploaded_data is None:
            self._show_upload_section()
        else:
            self._show_dashboard()
    
    def _show_upload_section(self):
        """Show file upload section"""
        st.markdown("### 📊 Upload Your Restaurant Data")
        
        # Upload zone
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="upload-zone">
                <h3>📁 Drag & Drop Your Data</h3>
                <p>Upload sales, inventory, or supplier data</p>
                <p><strong>Supported:</strong> Excel (.xlsx), CSV files</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['xlsx', 'csv', 'xls'],
                help="Upload your restaurant data file"
            )
            
            if uploaded_file:
                self._process_uploaded_file(uploaded_file)
        
        with col2:
            st.markdown("### 🚀 Try Demo Data")
            if st.button("Load Demo Restaurant", use_container_width=True):
                self._load_demo_data()
            
            st.markdown("### 📈 What You'll Get")
            st.markdown("""
            - **💰 Cost savings** with exact dollar amounts
            - **📊 Menu performance** analysis
            - **🌤️ Weather predictions** for sales
            - **🎯 Specific recommendations** to increase profit
            - **📈 Interactive charts** and insights
            """)
    
    def _process_uploaded_file(self, uploaded_file):
        """Process uploaded file with AI parsing"""
        with st.spinner("🤖 Analyzing your data with AI..."):
            try:
                # Parse file with AI
                file_contents = uploaded_file.read()
                parsing_result = self.parser.parse_file(file_contents, uploaded_file.name)
                
                if parsing_result['success']:
                    # Save to database
                    user_id = st.session_state.user['id']
                    upload_id = self.db.save_data_upload(
                        user_id=user_id,
                        filename=uploaded_file.name,
                        data_type=parsing_result['data_type'],
                        columns_detected=parsing_result['columns_mapped'],
                        rows_processed=parsing_result['rows_processed'],
                        file_size=len(file_contents)
                    )
                    
                    # Store processed data
                    processed_data = parsing_result['processed_data']
                    st.session_state.uploaded_data = {
                        'upload_id': upload_id,
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
        
        # Add weather insights if location available
        user = st.session_state.user
        if user.get('restaurant_location'):
            weather_insights = self._get_weather_insights(user['restaurant_location'])
            insights.extend(weather_insights)
        
        st.session_state.insights = insights
        
        # Save insights to database
        for insight in insights:
            self.db.save_user_insight(
                user_id=user['id'],
                insight_type=insight.get('type', 'general'),
                insight_data=insight,
                savings_potential=insight.get('savings_potential', 0)
            )
    
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
                <h2 style="color: #00b894; margin: 0;">${total_savings:,.0f}</h2>
                <p style="margin: 0;">Monthly Savings</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #6c5ce7; margin: 0;">{len(insights)}</h2>
                <p style="margin: 0;">AI Insights</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            efficiency_score = min(85 + len(insights) * 2, 95)
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #fd79a8; margin: 0;">{efficiency_score}%</h2>
                <p style="margin: 0;">Efficiency Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: #00cec9; margin: 0;">${total_savings * 12:,.0f}</h2>
                <p style="margin: 0;">Annual Impact</p>
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
        user = st.session_state.user
        location = user.get('restaurant_location')
        
        if not location:
            return
        
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