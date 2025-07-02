import streamlit as st
import pandas as pd
import numpy as np
import database
import plotly.express as px
from data_warehouse import DataWarehouse, get_sample_data

# Set theme settings
st.set_page_config(layout="wide", initial_sidebar_state="auto", page_title="Restaurant AI App")
st.sidebar.title("Navigation")
st.sidebar.markdown("""
    <style>
        [data-testid="stSidebarNav"] ul {
            margin-top: 0px;
        }
        [data-testid="stSidebarNav"] ul li a .baseLabel {
            text-shadow: none;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

class RestaurantApp:
    def __init__(self):
        self.warehouse = DataWarehouse()
        self.menu = ["Dashboard", "Data Upload", "Profit Analysis", "Inventory Management", "Forecasting"]
        self.selected_menu = st.sidebar.radio("", self.menu, 0)
    
    def run(self):
        if self.selected_menu == "Dashboard":
            self.show_dashboard()
        elif self.selected_menu == "Data Upload":
            self.process_file_upload()
        # Additional pages implemented below...

    def show_dashboard(self):
        ### Revenue Trends Analysis
        st.markdown("## 1️. Revenue Trends") # Added proper section marker
        revenue_data = self.warehouse.get_table("revenue_data")
        fig_revenue = px.line(revenue_data, x="day", y="revenue", title="Daily Revenue", 
                              labels={"revenue": "$ Revenue", "day": "Days"},
                              template="plotly_white")  # Fixed label references
        st.plotly_chart(fig_revenue, use_container_width=True)

        ### Profit Trends Analysis
        st.markdown("## 2️. Profit Trends") # Added correct section title
        profit_data = self.warehouse.get_table("profit_data")
        fig_profit = px.line(profit_data, x="day", y=["gross_profit"], labels={
            "gross_profit": "Gross Profit ($)",
            "day": "Time Period"  # Adjusted label reference
        }, title="Historical Profits Overview", width=800, height=500)
        st.plotly_chart(fig_profit, use_container_width=True)

        # Key metric display
        profit_margin = round(profit_data['gross_profit'].mean(), 2)
        metric_container = st.container()
        with metric_container:
            col1, col2 = st.columns([6, 4])
            col1.metric("**Profitability Score**", f"{profit_margin}% of revenue", "vs. last 30 days 22.54%")
            # Removed duplicate metric_container ref to fix error

    def process_file_upload(self):
        st.write("**3️. Upload Data** (sales, inventory, suppliers)")  # Corrected section heading
        uploaded_file = st.file_uploader("Drag & Drop CSV/Excel File", type=["csv", "xls", "xlsx"])
        if uploaded_file is not None:
            source_type = st.radio("Data Type", ["Sales Transactions", "Inventory Levels", "Supplier Quotes"])
            st.button("Process This File", type="primary", key="process_button_1", on_click=lambda: (
                self.warehouse.process_file(uploaded_file, source_type) if uploaded_file else None))
            # Fixed process_button_1 key conflict
            if uploaded_file and st.button("Process This File", type="primary", key="process_button_2", 
                                           help="Click to analyze using advanced AI"):
                process_result = self.warehouse.process_file(uploaded_file, source_type)
                database.save_processed_data(process_result['data'])
                self.warehouse.calculate_kpis(process_result['data'])
                st.success(f"Processed {len(process_result['data'])} rows of {source_type} data")
                # Added save_processed_data DB call
            else:
                st.info("Waiting for file upload to process") 
                # Fix: Use help parameter for button instructions
        
    # Additional methods like generate_report() and analytics_insights() will be added here

if __name__ == "__main__":
    RestaurantApp().run()
    
# Database functions and other helper methods would follow below...
