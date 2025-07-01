import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from typing import Dict, List, Optional
import io

# Page configuration
st.set_page_config(
    page_title="Restaurant Analytics Pro",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium UI styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main container */
    .main-container {
        background: white;
        margin: 2rem;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        min-height: 80vh;
    }
    
    /* Header */
    .app-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: #666;
        font-weight: 400;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .card-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }
    
    /* Metrics */
    .metric-row {
        display: flex;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        flex: 1;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Insights */
    .insight {
        background: #f8fafc;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 0 8px 8px 0;
    }
    
    .insight-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .insight-text {
        color: #666;
        line-height: 1.6;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader */
    .stFileUploader {
        background: #f8fafc;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.8rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Success messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

class ClaudeAI:
    """Placeholder for Claude AI integration - ready for future activation"""
    
    def __init__(self):
        # Ready for API key integration
        self.api_key = None
        self.client = None
        
    def analyze_complex_data(self, data, query):
        """Placeholder for complex AI analysis"""
        return {
            'available': False,
            'message': 'Advanced AI analysis coming soon! Currently using smart pattern detection.',
            'fallback_used': True
        }

class RestaurantAnalytics:
    def __init__(self):
        self.claude = ClaudeAI()
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'insights' not in st.session_state:
            st.session_state.insights = []
    
    def run(self):
        """Main app entry point"""
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown('''
        <div class="app-header">
            <div class="app-title">🍽️ Restaurant Analytics Pro</div>
            <div class="app-subtitle">Turn your restaurant data into actionable profits</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Main content
        if st.session_state.data is None:
            self.show_upload_page()
        else:
            self.show_dashboard()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_upload_page(self):
        """Show file upload interface"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('''
            <div class="card">
                <div class="card-title">📊 Upload Your Restaurant Data</div>
                <p style="color: #666; margin-bottom: 2rem;">
                    Upload your sales data, inventory reports, or any restaurant CSV/Excel files to get instant insights.
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose your file",
                type=['csv', 'xlsx', 'xls'],
                help="Upload sales data, inventory, or any restaurant data file"
            )
            
            if uploaded_file:
                self.process_file(uploaded_file)
            
            st.markdown("---")
            
            # Demo data option
            st.markdown('''
            <div class="card">
                <div class="card-title">🚀 Try Demo Data</div>
                <p style="color: #666; margin-bottom: 1.5rem;">
                    See the platform in action with realistic restaurant data
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("LOAD DEMO RESTAURANT DATA", use_container_width=True):
                self.load_demo_data()
    
    def process_file(self, file):
        """Process uploaded file"""
        try:
            with st.spinner("🔍 Analyzing your data..."):
                # Read file
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Store data
                st.session_state.data = {
                    'filename': file.name,
                    'dataframe': df,
                    'rows': len(df),
                    'columns': list(df.columns)
                }
                
                # Generate insights
                self.generate_insights(df)
                
                st.success(f"✅ Successfully processed {file.name} ({len(df)} rows)")
                st.rerun()
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    def load_demo_data(self):
        """Load demonstration data"""
        demo_data = pd.DataFrame({
            'Item': ['Classic Burger', 'Caesar Salad', 'Margherita Pizza', 'Grilled Salmon', 
                    'Chicken Wings', 'Fish Tacos', 'Craft Beer', 'House Wine', 'Chocolate Cake'],
            'Quantity': [45, 12, 28, 22, 35, 19, 67, 31, 15],
            'Price': [16.99, 14.99, 18.99, 24.99, 12.99, 15.99, 6.99, 8.99, 7.99],
            'Revenue': [764.55, 179.88, 531.72, 549.78, 454.65, 303.81, 468.33, 278.69, 119.85],
            'Category': ['Entrees', 'Salads', 'Pizza', 'Entrees', 'Appetizers', 
                        'Entrees', 'Beverages', 'Beverages', 'Desserts']
        })
        
        st.session_state.data = {
            'filename': 'Demo Restaurant Data',
            'dataframe': demo_data,
            'rows': len(demo_data),
            'columns': list(demo_data.columns)
        }
        
        self.generate_insights(demo_data)
        st.success("🎉 Demo data loaded! Explore your restaurant insights.")
        st.rerun()
    
    def generate_insights(self, df):
        """Generate business insights from data"""
        insights = []
        
        # Revenue insights
        if 'Revenue' in df.columns and 'Item' in df.columns:
            top_item = df.loc[df['Revenue'].idxmax(), 'Item']
            top_revenue = df['Revenue'].max()
            total_revenue = df['Revenue'].sum()
            
            insights.append({
                'type': 'revenue',
                'title': f'💰 {top_item} is your profit champion',
                'text': f'This superstar generated ${top_revenue:.2f} in revenue - that\'s {(top_revenue/total_revenue*100):.1f}% of your total sales!'
            })
        
        # Quantity insights
        if 'Quantity' in df.columns and 'Item' in df.columns:
            top_seller = df.loc[df['Quantity'].idxmax(), 'Item']
            top_quantity = df['Quantity'].max()
            
            insights.append({
                'type': 'popularity',
                'title': f'🔥 {top_seller} flies off the menu',
                'text': f'With {top_quantity} units sold, this is clearly a customer favorite. Consider featuring it prominently or creating variations.'
            })
        
        # Category insights
        if 'Category' in df.columns and 'Revenue' in df.columns:
            category_revenue = df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
            top_category = category_revenue.index[0]
            category_total = category_revenue.iloc[0]
            
            insights.append({
                'type': 'category',
                'title': f'🏆 {top_category} category dominates',
                'text': f'Your {top_category} items generated ${category_total:.2f} in revenue. Double down on this winning category!'
            })
        
        # Performance insights
        if 'Revenue' in df.columns and 'Quantity' in df.columns:
            df['AvgPrice'] = df['Revenue'] / df['Quantity']
            low_performers = df[df['Quantity'] < df['Quantity'].mean() * 0.7]
            
            if not low_performers.empty:
                insights.append({
                    'type': 'optimization',
                    'title': f'📉 {len(low_performers)} items need attention',
                    'text': f'Items like {low_performers.iloc[0]["Item"]} are underperforming. Consider promotions, recipe improvements, or menu optimization.'
                })
        
        st.session_state.insights = insights
    
    def show_dashboard(self):
        """Show main dashboard"""
        data = st.session_state.data
        df = data['dataframe']
        
        # Header with file info
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'''
            <div class="card">
                <div class="card-title">📄 {data['filename']}</div>
                <p style="color: #666;">Analyzing {data['rows']} rows of restaurant data</p>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            if st.button("⬆️ Upload New File"):
                st.session_state.data = None
                st.session_state.insights = []
                st.rerun()
        
        # Key metrics
        if 'Revenue' in df.columns:
            total_revenue = df['Revenue'].sum()
            avg_price = df['Revenue'].mean() if len(df) > 0 else 0
            total_items = len(df)
            total_quantity = df['Quantity'].sum() if 'Quantity' in df.columns else len(df)
            
            st.markdown(f'''
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-value">${total_revenue:,.0f}</div>
                    <div class="metric-label">Total Revenue</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_items}</div>
                    <div class="metric-label">Menu Items</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_quantity:,.0f}</div>
                    <div class="metric-label">Units Sold</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${avg_price:.2f}</div>
                    <div class="metric-label">Avg Revenue</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["💡 Smart Insights", "📊 Data Analysis", "🤖 AI Assistant"])
        
        with tab1:
            self.show_insights_tab()
        
        with tab2:
            self.show_analysis_tab()
        
        with tab3:
            self.show_ai_tab()
    
    def show_insights_tab(self):
        """Show generated insights"""
        if st.session_state.insights:
            for insight in st.session_state.insights:
                st.markdown(f'''
                <div class="insight">
                    <div class="insight-title">{insight['title']}</div>
                    <div class="insight-text">{insight['text']}</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No insights generated yet. Upload data to see smart recommendations!")
    
    def show_analysis_tab(self):
        """Show data analysis and charts"""
        df = st.session_state.data['dataframe']
        
        # Data preview
        st.markdown('''
        <div class="card">
            <div class="card-title">📋 Data Preview</div>
        </div>
        ''', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        
        # Charts
        if 'Revenue' in df.columns and 'Item' in df.columns:
            st.markdown('''
            <div class="card">
                <div class="card-title">📈 Revenue by Item</div>
            </div>
            ''', unsafe_allow_html=True)
            
            fig = px.bar(
                df.nlargest(10, 'Revenue'), 
                x='Item', 
                y='Revenue',
                title="Top 10 Items by Revenue",
                color='Revenue',
                color_continuous_scale='viridis'
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family="Inter"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if 'Category' in df.columns and 'Revenue' in df.columns:
            st.markdown('''
            <div class="card">
                <div class="card-title">🥧 Revenue by Category</div>
            </div>
            ''', unsafe_allow_html=True)
            
            category_data = df.groupby('Category')['Revenue'].sum().reset_index()
            fig = px.pie(
                category_data, 
                values='Revenue', 
                names='Category',
                title="Revenue Distribution by Category"
            )
            fig.update_layout(font_family="Inter")
            st.plotly_chart(fig, use_container_width=True)
    
    def show_ai_tab(self):
        """Show AI assistant interface"""
        st.markdown('''
        <div class="card">
            <div class="card-title">🤖 AI-Powered Analysis</div>
            <p style="color: #666; margin-bottom: 2rem;">
                Ask questions about your restaurant data and get intelligent insights powered by advanced AI.
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Sample questions
        st.markdown("**Try these questions:**")
        col1, col2 = st.columns(2)
        
        questions = [
            "What are my best performing items?",
            "Which categories drive the most revenue?",
            "What items should I promote more?",
            "How can I optimize my menu pricing?"
        ]
        
        for i, question in enumerate(questions):
            with col1 if i % 2 == 0 else col2:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    self.handle_ai_question(question)
        
        # Custom question
        user_question = st.text_area(
            "Or ask your own question:",
            placeholder="Example: How can I increase my profit margins?",
            height=100
        )
        
        if st.button("🚀 Get AI Insights", type="primary") and user_question:
            self.handle_ai_question(user_question)
    
    def handle_ai_question(self, question):
        """Handle AI questions with smart fallback"""
        df = st.session_state.data['dataframe']
        
        # Try Claude AI first (placeholder)
        ai_result = self.claude.analyze_complex_data(df, question)
        
        if not ai_result['available']:
            # Smart fallback analysis
            answer = self.smart_analysis_fallback(question, df)
            
            st.info("🧠 AI Analysis (Smart Pattern Detection)")
            st.markdown(f'''
            <div class="insight">
                <div class="insight-title">Answer: {question}</div>
                <div class="insight-text">{answer}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.caption("💡 Advanced AI analysis coming soon - currently using intelligent pattern detection")
    
    def smart_analysis_fallback(self, question, df):
        """Smart pattern-based analysis"""
        question_lower = question.lower()
        
        # Best performers
        if any(word in question_lower for word in ['best', 'top', 'performing']):
            if 'Revenue' in df.columns and 'Item' in df.columns:
                top_item = df.loc[df['Revenue'].idxmax(), 'Item']
                top_revenue = df['Revenue'].max()
                return f"Your best performer is **{top_item}** with ${top_revenue:.2f} in revenue. This item is clearly resonating with customers and should be prominently featured."
        
        # Category analysis
        elif any(word in question_lower for word in ['category', 'categories']):
            if 'Category' in df.columns and 'Revenue' in df.columns:
                cat_analysis = df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
                top_cat = cat_analysis.index[0]
                return f"**{top_cat}** is your strongest category, generating ${cat_analysis.iloc[0]:.2f} in revenue. Consider expanding this category or highlighting it more in your marketing."
        
        # Promotion suggestions
        elif any(word in question_lower for word in ['promote', 'marketing', 'boost']):
            if 'Revenue' in df.columns and 'Quantity' in df.columns:
                df['AvgPrice'] = df['Revenue'] / df['Quantity']
                high_price_low_volume = df[(df['AvgPrice'] > df['AvgPrice'].mean()) & (df['Quantity'] < df['Quantity'].mean())]
                if not high_price_low_volume.empty:
                    item = high_price_low_volume.iloc[0]['Item']
                    return f"Consider promoting **{item}** - it has good pricing but low volume. A targeted promotion could significantly boost revenue."
        
        # Pricing optimization
        elif any(word in question_lower for word in ['pricing', 'price', 'profit']):
            if 'Revenue' in df.columns and 'Quantity' in df.columns:
                df['AvgPrice'] = df['Revenue'] / df['Quantity']
                return f"Your average item price is ${df['AvgPrice'].mean():.2f}. Items like **{df.loc[df['AvgPrice'].idxmax(), 'Item']}** (${df['AvgPrice'].max():.2f}) show customers will pay premium prices for the right items."
        
        return "Based on your data patterns, I can see opportunities for optimization. Try asking more specific questions about revenue, categories, or individual items for detailed insights."

# Run the app
if __name__ == "__main__":
    app = RestaurantAnalytics()
    app.run()