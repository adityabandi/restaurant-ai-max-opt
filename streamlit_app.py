import streamlit as st
import pandas as pd
from enhanced_excel_parser import EnhancedExcelParser
from hybrid_ai_system import SmartAnalytics
import database
import datetime

# Helper class for data handling
class FileDataSource:
    def __init__(self, name: str, file_size: int, data_type: str='sale'):
        self.name = name
        self.file_size = file_size
        self.data_type = data_type
        self.insights = []
    
    def add_insight(self, category: str, details: str, confidence: float=0.8):
        self.insights.append({
            'category': category,
            'details': details,
            'confidence': confidence,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    def to_dict(self):
        return {
            'name': self.name,
            'size': self.file_size,
            'data_type': self.data_type,
            'insights': self.insights
        }

# Main Application
class RestaurantApp:
    def __init__(self):
        self.parser = EnhancedExcelParser()
        self.analytics = SmartAnalytics()
        st.sidebar.title('Navigation')
        self.page = st.sidebar.radio('Go to', [
            'Dashboard',
            'File Upload',
            'Insights',
            'Inventory Management'
        ]).lower().replace(' ', '_')

    def show_dashboard(self):
        st.title('📊 Restaurant Analytics Dashboard')
        
        # Load historical uploads
        uploads = database.get_uploaded_files()
        st.sidebar.subheader('Upload History')
        for upload in uploads:
            st.sidebar.markdown(f"- **{upload.upload_time}**: {upload.name} ({upload.file_size/1024:.2f} KB)")

        # Revenue Metrics
        st.header('Revenue Metrics')
        revenue_data = {"labels": ["Breakfast", "Lunch", "Dinner"], "data": [12000, 25000, 20000]}
        revenue_chart = st.line_chart(revenue_data, height=375)

        # Profit Margin Insights
        st.header('Profit Margin Insights')
        profit_comparison = pd.DataFrame({
            "Week": ["W1", "W2", "W3"],
            "Labor": [7200, 6800, 7500],
            "Food Cost": [5000, 5100, 4800],
            "Gross Profit": [15500, 15200, 15750]
        }) 
        st.bar_chart(profit_comparison, width=910)
        
    def show_file_upload(self):
        st.title("🗃️ Data Upload & Processing")
        uploaded_file = st.file_uploader("📂 Choose a file", type=["csv", "xlsx", "xls"])

        if uploaded_file:
            st.spinner('Processing...')
            
            # Store uploaded file metadata in database
            uploaded_data = FileDataSource(name=uploaded_file.name, file_size=len(uploaded_file.getvalue()))
            file_id = database.add_uploaded_file(uploaded_data.name, uploaded_data.file_size, uploaded_data.data_type)
            
            # Parse file
            parse_result = self.parser.parse_file(uploaded_file.getvalue(), uploaded_file.name)

            # Handle parsing errors
            if not parse_result['success']:
                database.log_error(file_id, parse_result.get('error', 'Unknown error'))
                if parse_result.get('error'):
                    st.error(f"File processing error: {parse_result['error']}")
                return
            
            uploaded_data.add_insight('File Parsing', f"Successfully parsed {len(parse_result['processed_data'])} rows", 0.95)
            database.log_insight(file_id, 'File Parsing', 'File parsing successful', 0.95)

            # Show parsed data
            st.markdown('**Processed Data Preview:**')
            st.dataframe(parse_result['processed_data'].head())
            st.json(parse_result['column_mapping'])

            # Store processed data to warehouse
            warehouse_id = database.add_dataset(
                name=uploaded_data.name,
                size=uploaded_data.file_size,
                data=parse_result['processed_data']
            )
            
            # Automated analysis
            analysis_result = self.analytics.analyze_profit_opportunities(parse_result['processed_data'])
            if analysis_result['success']:
                st.markdown('**SmartAnalytics Insights:**')
                insights = analysis_result['insights']
                st.json(insights)
                
                # Record each insight
                for insight_type, insight_details in insights.items():
                    uploaded_data.add_insight(insight_type, str(insight_details))
                    database.log_insight(file_id, insight_type, str(insight_details), analysis_result['confidence'])
            else:
                st.error('Error generating insights', analysis_result['error'])
                
    def show_inventory(self):
        st.title('⚙️ Inventory Management')
        st.markdown("Integrate with third-party inventory systems here (Square, Toast, etc)")

if __name__ == '__main__':
    app = RestaurantApp()
    action_mapping = {
        "dashboard": app.show_dashboard,
        "file_upload": app.show_file_upload,
        "insights": app.app.show_insights(), # <- Fix typo to use proper method name
        "inventory_management": app.show_inventory
    }
    action_mapping[app.page]()
