import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import json
import os
import numpy as np
from typing import Dict, List, Optional, Any

# Import our backend systems
try:
    from restaurant_analytics import RestaurantAnalytics
    from data_warehouse import RestaurantDataWarehouse
    from recipe_management import RecipeManagement
    from predictive_analytics import PredictiveAnalytics
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False

# Claude AI integration
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

class ClaudeAI:
    """Claude AI integration for restaurant profit optimization"""
    
    def __init__(self):
        self.client = None
        self.api_key = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Claude client with API key"""
        # Try to get API key from environment or Streamlit secrets
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key and hasattr(st, 'secrets'):
            try:
                self.api_key = st.secrets.get('ANTHROPIC_API_KEY')
            except:
                pass
        
        if self.api_key and CLAUDE_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                st.error(f"Claude AI initialization failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Claude AI is available"""
        return self.client is not None and CLAUDE_AVAILABLE
    
    def find_profit_leaks(self, data_summary: str) -> str:
        """Use Claude to identify profit leaks"""
        if not self.is_available():
            return "🔧 Claude AI not connected. Add your ANTHROPIC_API_KEY to get AI-powered profit analysis."
        
        prompt = f"""You are a restaurant profit expert. Analyze this data and find PROFIT LEAKS - things that are costing money RIGHT NOW.

RESTAURANT DATA:
{data_summary}

Focus on finding:
1. 🔴 CRITICAL PROFIT LEAKS (fix today to save money)
2. 💰 IMMEDIATE REVENUE OPPORTUNITIES (do this to make money now)
3. ⚠️ WARNING SIGNS (problems developing)
4. 🎯 TOP 3 ACTION ITEMS (specific things to do this week)

Be direct, specific, and focus on MONEY. Use dollar amounts when possible. Format with emojis and bullet points for quick scanning."""

        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1200,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error getting Claude analysis: {str(e)}"
    
    def optimize_menu_pricing(self, menu_data: str) -> str:
        """Use Claude to optimize menu pricing for maximum profit"""
        if not self.is_available():
            return "🔧 Claude AI not connected. Add your ANTHROPIC_API_KEY to get pricing optimization."
        
        prompt = f"""You are a restaurant pricing expert. Analyze this menu/sales data and recommend pricing changes to MAXIMIZE PROFIT.

MENU/SALES DATA:
{menu_data}

Provide:
1. 💰 PRICE INCREASES (items you can charge more for)
2. 🎯 BUNDLE OPPORTUNITIES (combinations that increase average ticket)
3. 🔥 PROMOTION STRATEGIES (items to push for higher profit)
4. ❌ MENU CUTS (unprofitable items to remove)
5. 💵 EXPECTED REVENUE IMPACT (estimate dollar gains)

Be specific with numbers and focus on immediate profit gains."""

        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error getting pricing analysis: {str(e)}"
    
    def smart_ordering_advice(self, inventory_data: str) -> str:
        """Use Claude for smart inventory ordering"""
        if not self.is_available():
            return "🔧 Claude AI not connected. Add your ANTHROPIC_API_KEY to get ordering recommendations."
        
        prompt = f"""You are a restaurant inventory expert. Analyze this data and provide SMART ORDERING advice to minimize waste and prevent stockouts.

INVENTORY DATA:
{inventory_data}

Provide:
1. 🚨 URGENT ORDERS (place orders today)
2. ⏰ UPCOMING NEEDS (order this week)
3. 🗑️ WASTE ALERTS (items going bad soon)
4. 💡 ORDERING OPTIMIZATION (better quantities/timing)
5. 💰 COST SAVINGS OPPORTUNITIES

Be specific with quantities and timing. Focus on preventing money loss."""

        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error getting ordering analysis: {str(e)}"

class RestaurantProfitMaximizer:
    """Main Restaurant Profit Maximizer App"""
    
    def __init__(self):
        # Initialize backend if available
        if BACKEND_AVAILABLE:
            self.analytics = RestaurantAnalytics()
        else:
            self.analytics = None
        
        self.claude = ClaudeAI()
        self.demo_data_loaded = False
        
    def load_premium_css(self):
        """Load premium profit-focused CSS"""
        st.markdown("""
        <style>
        /* Import premium fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Main app styling */
        .stApp {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Main container */
        .main-container {
            background: white;
            margin: 0.5rem;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }
        
        /* Header styling */
        .profit-header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            border-radius: 15px;
            color: white;
        }
        
        .profit-title {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .profit-subtitle {
            font-size: 1.3rem;
            opacity: 0.9;
        }
        
        /* Status cards */
        .status-card {
            background: linear-gradient(135deg, #00b894, #00a085);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,184,148,0.3);
        }
        
        .warning-card {
            background: linear-gradient(135deg, #fdcb6e, #e17055);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 8px 25px rgba(253,203,110,0.3);
        }
        
        .critical-card {
            background: linear-gradient(135deg, #d63031, #74b9ff);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 8px 25px rgba(214,48,49,0.3);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        /* Action cards */
        .action-card {
            background: linear-gradient(135deg, #6c5ce7, #a29bfe);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(108,92,231,0.3);
        }
        
        .profit-leak-card {
            background: linear-gradient(135deg, #ff6b6b, #feca57);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(255,107,107,0.3);
            border-left: 5px solid #ff3838;
        }
        
        .revenue-card {
            background: linear-gradient(135deg, #00b894, #55efc4);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(0,184,148,0.3);
            border-left: 5px solid #00b894;
        }
        
        /* Metrics styling */
        .big-metric {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            color: white;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(116,185,255,0.3);
        }
        
        .big-metric h1 {
            font-size: 3rem;
            margin: 0;
            font-weight: 700;
        }
        
        .big-metric p {
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #6c5ce7, #a29bfe);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(108,92,231,0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(108,92,231,0.6);
        }
        
        /* File uploader styling */
        .stFileUploader {
            border: 3px dashed #6c5ce7;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            background: linear-gradient(135deg, #f8f9ff, #e8e5ff);
        }
        
        /* Alert styling */
        .profit-alert {
            background: linear-gradient(135deg, #ff6b6b, #feca57);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            font-weight: 600;
            box-shadow: 0 5px 15px rgba(255,107,107,0.3);
        }
        
        .success-alert {
            background: linear-gradient(135deg, #00b894, #55efc4);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            font-weight: 600;
            box-shadow: 0 5px 15px rgba(0,184,148,0.3);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_profit_header(self):
        """Render the profit-focused header"""
        st.markdown("""
        <div class="profit-header">
            <div class="profit-title">💰 Restaurant Profit Maximizer</div>
            <div class="profit-subtitle">🤖 Powered by Claude AI • Find money leaks • Maximize profits • Get rich</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_claude_status(self):
        """Show Claude AI connection status"""
        if self.claude.is_available():
            st.markdown("""
            <div class="status-card">
                <h3>🤖 Claude AI Connected</h3>
                <p>Ready to analyze your profit opportunities</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-card">
                <h3>⚠️ Claude AI Not Connected</h3>
                <p>Add ANTHROPIC_API_KEY to unlock AI profit analysis</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_profit_dashboard(self):
        """Main profit dashboard"""
        st.markdown("## 🎯 Profit Control Center")
        
        # Always show demo option prominently
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="profit-alert">
                <h3>🚀 Ready to Find Money Leaks?</h3>
                <p>Load demo data to see how Claude AI can identify profit opportunities in your restaurant!</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🚀 Load Demo Data", key="demo_dashboard", type="primary"):
                self.load_demo_data()
                st.rerun()
        
        # Show profit metrics (demo version)
        self.render_demo_metrics()
        
        # Claude AI Analysis Section
        if self.claude.is_available():
            st.markdown("## 🤖 AI Profit Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 Find Profit Leaks", key="find_leaks"):
                    with st.spinner("🔍 Claude AI is hunting for profit leaks..."):
                        data_summary = self.prepare_demo_data_summary()
                        analysis = self.claude.find_profit_leaks(data_summary)
                        
                        st.markdown(f"""
                        <div class="profit-leak-card">
                            <h3>🔍 Profit Leak Analysis</h3>
                            <div style="white-space: pre-wrap;">{analysis}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                if st.button("💰 Optimize Menu Pricing", key="optimize_pricing"):
                    with st.spinner("💰 Claude AI is optimizing your pricing..."):
                        menu_data = self.prepare_demo_menu_data()
                        analysis = self.claude.optimize_menu_pricing(menu_data)
                        
                        st.markdown(f"""
                        <div class="revenue-card">
                            <h3>💰 Pricing Optimization</h3>
                            <div style="white-space: pre-wrap;">{analysis}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Smart ordering section
        st.markdown("## 📦 Smart Ordering Assistant")
        if st.button("📦 Get Ordering Recommendations"):
            if self.claude.is_available():
                with st.spinner("📦 Claude AI is analyzing inventory needs..."):
                    inventory_data = self.prepare_demo_inventory_data()
                    analysis = self.claude.smart_ordering_advice(inventory_data)
                    
                    st.markdown(f"""
                    <div class="action-card">
                        <h3>📦 Smart Ordering Recommendations</h3>
                        <div style="white-space: pre-wrap;">{analysis}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Connect Claude AI to get smart ordering recommendations")
    
    def render_demo_metrics(self):
        """Render realistic demo profit metrics"""
        st.markdown("### 📊 Your Restaurant at a Glance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="big-metric">
                <h1>$23,450</h1>
                <p>Revenue This Month</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="big-metric">
                <h1>31.2%</h1>
                <p>Food Cost % (HIGH!)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="big-metric">
                <h1>$42.80</h1>
                <p>Avg Transaction</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="big-metric">
                <h1>12.8%</h1>
                <p>Profit Margin (LOW!)</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Critical alerts
        st.markdown("""
        <div class="critical-card">
            <h3>🚨 CRITICAL: You're losing $1,247 per month!</h3>
            <p>Food cost is 31.2% - should be 25%. That's 6.2% overspend on $23,450 revenue.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-card">
            <h3>⚠️ 5 Items Running Low - Order Today!</h3>
            <p>Chicken breast, lettuce, tomatoes, onions, and cheese will run out by Thursday</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="profit-alert">
            <h3>💰 Revenue Opportunity: $890/month</h3>
            <p>Your burger is underpriced by $2. 150 burgers/month = easy $300. Plus 5 other opportunities...</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_smart_uploader(self):
        """Smart file uploader with profit focus"""
        st.markdown("## 📊 Upload Your Restaurant Data")
        st.markdown("**Upload your data to unlock AI-powered profit insights**")
        
        # Data type selection with profit context
        data_type_options = {
            'sales': '💰 Sales Data (POS exports, transaction logs)',
            'inventory': '📦 Inventory Data (stock levels, costs)',
            'menu': '🍽️ Menu Data (items, prices, costs)',
            'suppliers': '🚚 Supplier Data (costs, delivery times)',
            'labor': '👥 Labor Data (schedules, wages)'
        }
        
        selected_display = st.selectbox(
            "What type of data are you uploading?",
            list(data_type_options.values()),
            help="Choose the data type for best analysis"
        )
        
        # Get actual data type
        data_type = [k for k, v in data_type_options.items() if v == selected_display][0]
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Choose your file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload CSV or Excel files. We'll automatically detect and clean your data."
        )
        
        if uploaded_file:
            df = self.process_uploaded_file(uploaded_file, data_type)
            if df is not None:
                # Show data preview
                st.markdown("### 📋 Data Preview")
                st.dataframe(df.head(10))
                
                # Calculate and show profit metrics
                metrics = self.calculate_profit_metrics(df, data_type)
                
                if metrics:
                    st.markdown("### 💰 Instant Profit Insights")
                    
                    if data_type == 'sales':
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Revenue", f"${metrics.get('total_revenue', 0):,.2f}")
                        with col2:
                            st.metric("Avg Transaction", f"${metrics.get('avg_transaction', 0):.2f}")
                        with col3:
                            st.metric("Transaction Count", f"{metrics.get('transaction_count', 0):,}")
                        
                        # Pareto analysis
                        if 'pareto_ratio' in metrics:
                            pareto = metrics['pareto_ratio']
                            if pareto > 80:
                                st.markdown(f"""
                                <div class="profit-alert">
                                    <strong>⚠️ Menu Optimization Opportunity!</strong><br>
                                    {pareto:.1f}% of revenue comes from your top 20% of items. 
                                    Consider promoting these high-performers and removing underperformers.
                                </div>
                                """, unsafe_allow_html=True)
                
                # Claude AI analysis for uploaded data
                if self.claude.is_available():
                    st.markdown("### 🤖 Ask Claude AI About This Data")
                    
                    user_question = st.text_area(
                        "What would you like to know?",
                        placeholder="e.g., 'How can I increase profit from this data?' or 'What items should I promote?'",
                        height=80
                    )
                    
                    if st.button("🔍 Analyze with AI"):
                        if user_question:
                            with st.spinner("🤖 Claude AI is analyzing..."):
                                # Prepare data summary
                                data_summary = f"""
                                Data Type: {data_type}
                                Records: {len(df)}
                                Columns: {', '.join(df.columns)}
                                
                                Sample Data:
                                {df.head(5).to_string()}
                                
                                Key Metrics: {json.dumps(metrics, indent=2)}
                                """
                                
                                analysis = self.claude.find_profit_leaks(data_summary + f"\n\nSpecific Question: {user_question}")
                                
                                st.markdown(f"""
                                <div class="action-card">
                                    <h4>🤖 Claude AI Analysis</h4>
                                    <div style="white-space: pre-wrap;">{analysis}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("Please enter a question for analysis.")
                
                return df, data_type
        
        return None, None
    
    def process_uploaded_file(self, uploaded_file, data_type: str) -> Optional[pd.DataFrame]:
        """Process uploaded file with smart detection"""
        try:
            # Read file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("❌ Unsupported file format. Upload CSV or Excel files.")
                return None
            
            # Smart data cleanup
            df = self.smart_data_cleanup(df, data_type)
            
            st.markdown(f"""
            <div class="success-alert">
                ✅ Processed {len(df)} records • Ready for profit analysis
            </div>
            """, unsafe_allow_html=True)
            
            return df
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            return None
    
    def smart_data_cleanup(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Smart data cleanup and standardization"""
        # Remove empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Smart column detection and renaming
        if data_type == 'sales':
            # Try to detect common sales columns
            for col in df.columns:
                col_lower = col.lower()
                if any(word in col_lower for word in ['total', 'amount', 'price', 'revenue']):
                    if 'total_amount' not in df.columns:
                        df = df.rename(columns={col: 'total_amount'})
                elif any(word in col_lower for word in ['date', 'time', 'timestamp']):
                    if 'date' not in df.columns:
                        df = df.rename(columns={col: 'date'})
                elif any(word in col_lower for word in ['item', 'product', 'name']):
                    if 'item_name' not in df.columns:
                        df = df.rename(columns={col: 'item_name'})
                elif any(word in col_lower for word in ['qty', 'quantity', 'count']):
                    if 'quantity' not in df.columns:
                        df = df.rename(columns={col: 'quantity'})
        
        # Convert date columns
        if 'date' in df.columns:
            try:
                df['date'] = pd.to_datetime(df['date'])
            except:
                pass
        
        # Convert numeric columns
        numeric_cols = ['total_amount', 'quantity', 'cost', 'price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def calculate_profit_metrics(self, df: pd.DataFrame, data_type: str) -> Dict:
        """Calculate key profit metrics"""
        metrics = {}
        
        if data_type == 'sales' and 'total_amount' in df.columns:
            metrics['total_revenue'] = df['total_amount'].sum()
            metrics['avg_transaction'] = df['total_amount'].mean()
            metrics['transaction_count'] = len(df)
            
            # Item analysis
            if 'item_name' in df.columns:
                item_sales = df.groupby('item_name')['total_amount'].sum().sort_values(ascending=False)
                if len(item_sales) > 0:
                    metrics['top_item'] = item_sales.index[0]
                    metrics['top_item_revenue'] = item_sales.iloc[0]
                    
                    # Pareto analysis
                    total_items = len(item_sales)
                    top_20_percent = max(1, int(total_items * 0.2))
                    top_20_revenue = item_sales.head(top_20_percent).sum()
                    metrics['pareto_ratio'] = (top_20_revenue / metrics['total_revenue']) * 100 if metrics['total_revenue'] > 0 else 0
        
        return metrics
    
    def load_demo_data(self):
        """Load realistic demo data"""
        try:
            self.demo_data_loaded = True
            st.success("✅ Demo data loaded! Navigate to other sections to see AI analysis.")
        except Exception as e:
            st.error(f"❌ Error loading demo data: {str(e)}")
    
    def prepare_demo_data_summary(self) -> str:
        """Prepare realistic demo data summary for Claude"""
        return """
        Restaurant: "Bella's Bistro" - Italian casual dining
        Location: Downtown, high foot traffic area
        Seats: 45, Average 120 customers/day
        
        CURRENT FINANCIAL METRICS:
        - Monthly Revenue: $23,450
        - Food Cost: 31.2% (TARGET: 25% - OVERSPENDING $1,247/month)
        - Labor Cost: 28.5% (acceptable range)
        - Average Transaction: $42.80
        - Transactions/day: ~18
        - Profit Margin: 12.8% (LOW - should be 15-18%)
        
        TOP SELLING ITEMS (Last 30 days):
        1. Margherita Pizza - $16.99 (Cost: $6.20) - 89 sold
        2. Chicken Alfredo - $18.99 (Cost: $7.80) - 76 sold
        3. Caesar Salad - $12.99 (Cost: $4.50) - 67 sold
        4. Lasagna - $19.99 (Cost: $8.90) - 52 sold
        5. Tiramisu - $8.99 (Cost: $2.80) - 45 sold
        
        UNDERPERFORMING ITEMS:
        - Seafood Risotto: $24.99 (Cost: $12.40) - Only 8 sold
        - Veal Parmigiana: $26.99 (Cost: $14.20) - Only 6 sold
        
        INVENTORY ALERTS:
        - Chicken breast: 12 lbs remaining (3-day supply)
        - Mozzarella cheese: 8 lbs remaining (2-day supply)  
        - Fresh basil: 2 bunches (1-day supply)
        - Tomatoes: 15 lbs (4-day supply)
        - Heavy cream: 3 quarts (2-day supply)
        
        WASTE ISSUES:
        - 8% food waste (industry average 4-6%)
        - Seafood items often expire unused
        - Prep portions inconsistent
        
        LABOR INEFFICIENCIES:
        - Weekend overstaffing (3 extra hours/day)
        - Slow ticket times during rush (avg 18 min, should be 12)
        
        REVENUE OPPORTUNITIES:
        - Burger underpriced by $2 vs competitors
        - No dessert upselling program
        - Limited wine pairings promoted
        - No lunch specials to drive weekday traffic
        """
    
    def prepare_demo_menu_data(self) -> str:
        """Prepare demo menu data for pricing analysis"""
        return """
        BELLA'S BISTRO MENU ANALYSIS
        
        APPETIZERS:
        - Bruschetta: $8.99 (Cost: $2.10) - 76% margin - 34 sold/month
        - Calamari: $11.99 (Cost: $4.20) - 65% margin - 28 sold/month
        - Antipasto: $13.99 (Cost: $5.80) - 58% margin - 22 sold/month
        
        ENTREES:
        - Margherita Pizza: $16.99 (Cost: $6.20) - 63% margin - 89 sold ⭐ BESTSELLER
        - Chicken Alfredo: $18.99 (Cost: $7.80) - 59% margin - 76 sold ⭐ POPULAR
        - Lasagna: $19.99 (Cost: $8.90) - 55% margin - 52 sold
        - Caesar Salad: $12.99 (Cost: $4.50) - 65% margin - 67 sold
        - Seafood Risotto: $24.99 (Cost: $12.40) - 50% margin - 8 sold ❌ UNDERPERFORMER
        - Veal Parmigiana: $26.99 (Cost: $14.20) - 47% margin - 6 sold ❌ UNDERPERFORMER
        
        DESSERTS:
        - Tiramisu: $8.99 (Cost: $2.80) - 69% margin - 45 sold
        - Gelato: $6.99 (Cost: $1.90) - 73% margin - 32 sold
        - Cannoli: $7.99 (Cost: $2.40) - 70% margin - 28 sold
        
        BEVERAGES:
        - House Wine (glass): $7.99 (Cost: $2.20) - 72% margin
        - Beer: $4.99 (Cost: $1.80) - 64% margin  
        - Soft Drinks: $2.99 (Cost: $0.45) - 85% margin
        
        COMPETITOR PRICING:
        - Similar pizzas: $18-20 (we're $2 under)
        - Pasta dishes: $19-22 (competitive)
        - Appetizers: $9-14 (competitive)
        
        CURRENT ISSUES:
        - No bundling/combo deals
        - High-cost items not selling
        - Missing dessert upselling
        - Wine pairings not promoted
        """
    
    def prepare_demo_inventory_data(self) -> str:
        """Prepare demo inventory data for ordering analysis"""
        return """
        BELLA'S BISTRO INVENTORY STATUS
        Current Date: Today
        
        CRITICAL - ORDER TODAY:
        - Chicken Breast: 12 lbs (3-day supply, use 4 lbs/day)
        - Mozzarella Cheese: 8 lbs (2-day supply, use 4 lbs/day)
        - Fresh Basil: 2 bunches (1-day supply, use 2 bunches/day)
        
        WARNING - ORDER THIS WEEK:
        - Tomatoes: 15 lbs (4-day supply, use 3.5 lbs/day)
        - Heavy Cream: 3 quarts (2-day supply, use 1.5 quarts/day)
        - Ground Beef: 20 lbs (5-day supply, use 4 lbs/day)
        - Parmesan Cheese: 6 lbs (4-day supply, use 1.5 lbs/day)
        
        WASTE ALERTS:
        - Seafood (salmon): 3 lbs expiring in 2 days - only sold 1 seafood dish this week
        - Arugula: 2 lbs expiring tomorrow - low salad sales
        
        OVERSTOCKED:
        - Pasta (dried): 45 lbs (30-day supply)
        - Olive Oil: 8 bottles (45-day supply)
        - Canned Tomatoes: 24 cans (20-day supply)
        
        SUPPLIER INFO:
        - Main supplier delivery: Tuesday/Friday
        - Minimum order: $150
        - Lead time: Next day for regular items
        - Premium items (seafood): 48-hour notice
        
        ORDERING PATTERNS:
        - Weekends use 40% more ingredients
        - Chicken dishes spike on Tuesdays (special day)
        - Cheese consumption highest Thursday-Saturday
        
        COST OPTIMIZATION:
        - Bulk chicken: $4.80/lb vs $5.20/lb small orders
        - Cheese block vs shredded: 15% savings
        - Local tomatoes: 20% cheaper in season (now)
        """
    
    def run(self):
        """Main app runner"""
        st.set_page_config(
            page_title="Restaurant Profit Maximizer",
            page_icon="💰",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Load premium CSS
        self.load_premium_css()
        
        # Initialize session state
        if 'page' not in st.session_state:
            st.session_state['page'] = 'Dashboard'
        
        # Sidebar navigation
        with st.sidebar:
            st.markdown("## 💰 Profit Navigator")
            
            # Navigation buttons
            nav_options = {
                'Dashboard': '🎯 Profit Dashboard',
                'Upload Data': '📊 Upload Data', 
                'Profit Leaks': '🔍 Find Profit Leaks',
                'Smart Ordering': '📦 Smart Ordering',
                'Menu Optimizer': '🍽️ Menu Optimizer'
            }
            
            selected_nav = st.selectbox(
                "Navigate to:",
                list(nav_options.values()),
                index=list(nav_options.keys()).index(st.session_state['page']) if st.session_state['page'] in nav_options else 0
            )
            
            # Update session state
            st.session_state['page'] = [k for k, v in nav_options.items() if v == selected_nav][0]
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("## 📊 Quick Stats")
            st.metric("Monthly Revenue", "$23,450")
            st.metric("Food Cost %", "31.2% 🔴")
            st.metric("Profit Margin", "12.8%")
            
            st.markdown("---")
            self.render_claude_status()
            
            # Quick action buttons
            st.markdown("## ⚡ Quick Actions")
            if st.button("🚀 Load Demo Data", key="sidebar_demo"):
                self.load_demo_data()
                st.rerun()
        
        # Main content area
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Render header
        self.render_profit_header()
        
        # Route to different pages
        if st.session_state['page'] == 'Dashboard':
            self.render_profit_dashboard()
            
        elif st.session_state['page'] == 'Upload Data':
            self.render_smart_uploader()
            
        elif st.session_state['page'] == 'Profit Leaks':
            st.markdown("## 🔍 Profit Leak Detector")
            if self.claude.is_available():
                if st.button("🔍 Scan for Profit Leaks", type="primary"):
                    with st.spinner("🔍 Claude AI is scanning for profit leaks..."):
                        data_summary = self.prepare_demo_data_summary()
                        analysis = self.claude.find_profit_leaks(data_summary)
                        
                        st.markdown(f"""
                        <div class="profit-leak-card">
                            <h3>🔍 Comprehensive Profit Leak Analysis</h3>
                            <div style="white-space: pre-wrap;">{analysis}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Connect Claude AI to unlock profit leak detection")
                
        elif st.session_state['page'] == 'Smart Ordering':
            st.markdown("## 📦 Smart Ordering Assistant")
            if self.claude.is_available():
                if st.button("📦 Get Ordering Recommendations", type="primary"):
                    with st.spinner("📦 Claude AI is analyzing your inventory needs..."):
                        inventory_data = self.prepare_demo_inventory_data()
                        analysis = self.claude.smart_ordering_advice(inventory_data)
                        
                        st.markdown(f"""
                        <div class="action-card">
                            <h3>📦 Smart Ordering Recommendations</h3>
                            <div style="white-space: pre-wrap;">{analysis}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Connect Claude AI to unlock smart ordering")
                
        elif st.session_state['page'] == 'Menu Optimizer':
            st.markdown("## 🍽️ Menu Profit Optimizer")
            if self.claude.is_available():
                if st.button("💰 Optimize Menu for Maximum Profit", type="primary"):
                    with st.spinner("💰 Claude AI is optimizing your menu..."):
                        menu_data = self.prepare_demo_menu_data()
                        analysis = self.claude.optimize_menu_pricing(menu_data)
                        
                        st.markdown(f"""
                        <div class="revenue-card">
                            <h3>💰 Menu Optimization Strategy</h3>
                            <div style="white-space: pre-wrap;">{analysis}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Connect Claude AI to unlock menu optimization")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Initialize and run the app
if __name__ == "__main__":
    try:
        app = RestaurantProfitMaximizer()
        app.run()
    except Exception as e:
        st.error(f"💥 App startup failed: {str(e)}")
        st.markdown("## 🔧 Troubleshooting")
        st.markdown("1. Make sure all required files are present")
        st.markdown("2. Check that dependencies are installed")
        st.markdown("3. Add ANTHROPIC_API_KEY for AI features")