import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# ============================================================================
# MINIMAL TEST - Let's start super simple and build up
# ============================================================================

st.set_page_config(
    page_title="Restaurant Analytics Pro",
    page_icon="🍽️",
    layout="wide"
)

# Basic CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-container {
        background: white;
        margin: 2rem;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Super simple main function to test deployment"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("# 🍽️ Restaurant Analytics Pro")
    st.markdown("### Turn your restaurant data into actionable profits")
    
    # Test if we're running
    st.success("✅ App is running successfully!")
    
    # Simple file upload test
    st.markdown("## 📊 Upload Test")
    uploaded_file = st.file_uploader("Upload a CSV file", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ File loaded: {len(df)} rows, {len(df.columns)} columns")
            st.dataframe(df.head())
            
            # Simple chart test
            if len(df.columns) >= 2:
                st.markdown("## 📈 Chart Test")
                fig = px.bar(df.head(10), x=df.columns[0], y=df.columns[1])
                st.plotly_chart(fig)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Demo data test
    st.markdown("## 🎯 Demo Data Test")
    if st.button("Load Demo Data"):
        demo_data = pd.DataFrame({
            'Item': ['Burger', 'Pizza', 'Salad'],
            'Revenue': [100, 150, 75],
            'Quantity': [10, 8, 5]
        })
        
        st.success("✅ Demo data loaded!")
        st.dataframe(demo_data)
        
        # Demo chart
        fig = px.bar(demo_data, x='Item', y='Revenue')
        st.plotly_chart(fig)
    
    # Debug info
    st.markdown("## 🔍 Debug Info")
    st.write("Python version:", st.__version__)
    st.write("Pandas version:", pd.__version__)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"App Error: {str(e)}")
        st.write("Full error:", e)