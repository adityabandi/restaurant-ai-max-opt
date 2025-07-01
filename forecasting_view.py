import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ForecastingView:
    """View for forecasting and predictive analytics"""
    
    def __init__(self, analytics):
        self.analytics = analytics
    
    def show(self):
        """Show forecasting view"""
        st.markdown("## ud83dudcc8 Sales & Inventory Forecasting")
        
        # Check if we have the necessary data
        status = self.analytics.get_system_status()
        has_sales_data = status['predictive_analytics']['has_sales_data']
        has_inventory_data = status['predictive_analytics']['has_inventory_data']
        
        if not has_sales_data:
            st.warning("ud83dudea8 Sales data is required for forecasting. Please upload sales data first.")
            return
        
        # Create tabs for different forecasts
        tabs = ["ud83dudcc8 Sales Forecast"]
        if has_inventory_data:
            tabs.append("ud83dudcdc Inventory Forecast")
        
        selected_tabs = st.tabs(tabs)
        
        with selected_tabs[0]:  # Sales Forecast
            self._show_sales_forecast()
        
        if has_inventory_data and len(tabs) > 1:
            with selected_tabs[1]:  # Inventory Forecast
                self._show_inventory_forecast()
    
    def _show_sales_forecast(self):
        """Show sales forecast"""
        st.markdown("### Sales Forecast")
        
        # Parameters
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Select forecast horizon
            days_ahead = st.slider(
                "Forecast Horizon (Days)", 
                min_value=7, 
                max_value=30,
                value=14,
                step=1,
                help="Number of days to forecast into the future"
            )
        
        with col2:
            # Generate forecast button
            if st.button("Generate Forecast", type="primary", use_container_width=True):
                with st.spinner("Generating sales forecast..."):
                    forecast_result = self.analytics.generate_sales_forecast(days_ahead)
                    
                    if forecast_result['success']:
                        st.session_state.sales_forecast = forecast_result['forecast']
                        st.session_state.sales_forecast_id = forecast_result['forecast_id']
                        st.success("u2705 Forecast generated successfully!")
                    else:
                        st.error(f"u274c Error generating forecast: {forecast_result.get('error', 'Unknown error')}")
        
        # Show forecast if available
        if hasattr(st.session_state, 'sales_forecast') and st.session_state.sales_forecast:
            self._show_sales_forecast_results(st.session_state.sales_forecast)
        else:
            st.info("Click 'Generate Forecast' to create a sales forecast")
    
    def _show_sales_forecast_results(self, forecast_data: List[Dict]):
        """Show sales forecast results"""
        # Convert to DataFrame
        df = pd.DataFrame(forecast_data)
        
        # Add weekday names
        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.day_name()
        
        # Format date for display
        df['display_date'] = df['date'].dt.strftime('%a, %b %d')
        
        # Create summary metrics
        total_forecast = df['forecasted_amount'].sum()
        avg_daily = df['forecasted_amount'].mean()
        peak_day = df.loc[df['forecasted_amount'].idxmax()]
        peak_day_name = peak_day['display_date']
        peak_amount = peak_day['forecasted_amount']
        
        # Show summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Forecasted Sales",
                value=f"${total_forecast:,.0f}"
            )
        
        with col2:
            st.metric(
                label="Average Daily Sales",
                value=f"${avg_daily:,.0f}"
            )
        
        with col3:
            st.metric(
                label=f"Peak Day: {peak_day_name}",
                value=f"${peak_amount:,.0f}"
            )
        
        # Create forecast chart
        st.markdown("#### Daily Sales Forecast")
        
        fig = px.bar(
            df,
            x='display_date',
            y='forecasted_amount',
            color='weekday',
            title="Forecasted Daily Sales",
            labels={'forecasted_amount': 'Forecasted Sales ($)', 'display_date': 'Date'},
            text_auto='.2s'
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Forecasted Sales ($)",
            legend_title="Day of Week",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#1a1a1a',
            height=500,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Show seasonality heatmap
        st.markdown("#### Seasonality Analysis")
        
        # Group by weekday
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_df = df.copy()
        weekday_df['weekday_idx'] = weekday_df['weekday'].apply(lambda x: weekday_order.index(x))
        weekday_df = weekday_df.sort_values('weekday_idx')
        
        weekday_avg = weekday_df.groupby('weekday')['forecasted_amount'].mean().reset_index()
        weekday_avg['weekday_idx'] = weekday_avg['weekday'].apply(lambda x: weekday_order.index(x))
        weekday_avg = weekday_avg.sort_values('weekday_idx')
        
        # Calculate relative values
        overall_avg = weekday_avg['forecasted_amount'].mean()
        weekday_avg['relative'] = weekday_avg['forecasted_amount'] / overall_avg
        
        # Create heatmap data
        heatmap_data = []
        for _, row in weekday_avg.iterrows():
            heatmap_data.append([row['weekday'], "Relative Sales", row['relative']])
        
        heatmap_df = pd.DataFrame(heatmap_data, columns=['Weekday', 'Metric', 'Value'])
        
        # Create heatmap
        fig = px.imshow(
            heatmap_df.pivot(index='Weekday', columns='Metric', values='Value'),
            color_continuous_scale=[(0, "#e74c3c"), (0.5, "#f1c40f"), (1, "#2ecc71")],
            labels=dict(x="Metric", y="Weekday", color="Value"),
            text_auto='.2f',
            aspect="auto",
            height=300,
            title="Weekday Sales Pattern (Relative to Average)"
        )
        
        # Update layout
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#1a1a1a',
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Show factors breakdown
        st.markdown("#### Forecast Factors")
        
        # Prepare factors data
        factors_df = pd.DataFrame([
            {
                'date': day['date'],
                'display_date': pd.to_datetime(day['date']).strftime('%a, %b %d'),
                'Daily Pattern': day['factors']['daily'],
                'Monthly Pattern': day['factors']['monthly'],
                'Weekend Effect': day['factors']['weekend'],
                'External Factors': day['factors']['external']
            }
            for day in forecast_data
        ])
        
        # Create radar chart
        factors_list = ['Daily Pattern', 'Monthly Pattern', 'Weekend Effect', 'External Factors']
        
        # Create subplot
        fig = make_subplots(rows=1, cols=1)
        
        # Add line for each date
        for i, row in factors_df.iterrows():
            values = [row[f] for f in factors_list]
            values.append(values[0])  # Close the loop
            
            # Create label for the date
            date_label = row['display_date']
            
            # Add trace
            fig.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=factors_list + [factors_list[0]],  # Close the loop
                    name=date_label,
                    mode='lines+markers'
                )
            )
        
        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 2]  # Set range based on your factor values
                )
            ),
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#1a1a1a',
            height=500,
            margin=dict(l=10, r=10, t=40, b=10),
            title="Forecast Factors by Day"
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Show raw forecast data as table
        with st.expander("View Raw Forecast Data"):
            st.dataframe(df[['display_date', 'weekday', 'forecasted_amount']], use_container_width=True)
    
    def _show_inventory_forecast(self):
        """Show inventory forecast"""
        st.markdown("### Inventory Forecast")
        
        # Parameters
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Select forecast horizon
            days_ahead = st.slider(
                "Forecast Horizon (Days)", 
                min_value=7, 
                max_value=30,
                value=14,
                step=1,
                key="inventory_days_ahead",
                help="Number of days to forecast into the future"
            )
        
        with col2:
            # Generate forecast button
            if st.button("Generate Inventory Forecast", type="primary", use_container_width=True):
                with st.spinner("Generating inventory forecast..."):
                    forecast_result = self.analytics.generate_inventory_forecast(days_ahead)
                    
                    if forecast_result['success']:
                        st.session_state.inventory_forecast = forecast_result['forecast']
                        st.session_state.inventory_forecast_id = forecast_result['forecast_id']
                        st.success("u2705 Inventory forecast generated successfully!")
                    else:
                        st.error(f"u274c Error generating forecast: {forecast_result.get('error', 'Unknown error')}")
        
        # Show forecast if available
        if hasattr(st.session_state, 'inventory_forecast') and st.session_state.inventory_forecast:
            self._show_inventory_forecast_results(st.session_state.inventory_forecast)
        else:
            st.info("Click 'Generate Inventory Forecast' to create an inventory forecast")
    
    def _show_inventory_forecast_results(self, forecast_data: List[Dict]):
        """Show inventory forecast results"""
        # Summary statistics
        total_items = len(forecast_data)
        items_at_risk = sum(1 for item in forecast_data if item['days_remaining'] < 7)
        reorder_needed = sum(1 for item in forecast_data if item['reorder_needed'])
        
        # Show summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Items Tracked",
                value=f"{total_items}"
            )
        
        with col2:
            st.metric(
                label="Items at Risk",
                value=f"{items_at_risk}"
            )
        
        with col3:
            st.metric(
                label="Items Needing Reorder",
                value=f"{reorder_needed}"
            )
        
        # Show items at risk
        st.markdown("#### Inventory Risk Analysis")
        
        # Convert to DataFrame
        df = pd.DataFrame(forecast_data)
        
        # Generate status colors
        def get_status_color(days):
            if days < 3:
                return "#e74c3c"  # Red - Critical
            elif days < 7:
                return "#f39c12"  # Orange - Warning
            elif days < 14:
                return "#3498db"  # Blue - Monitor
            else:
                return "#2ecc71"  # Green - Good
        
        df['status_color'] = df['days_remaining'].apply(get_status_color)
        
        # Sort by days remaining
        df = df.sort_values('days_remaining')
        
        # Create inventory level chart
        fig = px.bar(
            df.head(15),  # Show top 15 most at-risk items
            y='item_name',
            x='days_remaining',
            orientation='h',
            color='days_remaining',
            color_continuous_scale=[(0, "#e74c3c"), (0.3, "#f39c12"), (0.5, "#3498db"), (1, "#2ecc71")],
            title="Days of Inventory Remaining by Item",
            labels={'days_remaining': 'Days Remaining', 'item_name': 'Item'},
            text='days_remaining'
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Days of Inventory Remaining",
            yaxis_title="Item",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color='#1a1a1a',
            height=500,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(autorange="reversed")  # Reverse y-axis to have most critical at top
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Show reorder recommendations
        st.markdown("#### Reorder Recommendations")
        
        # Filter items needing reorder
        reorder_df = df[df['reorder_needed']].copy()
        
        if not reorder_df.empty:
            # Create table for display
            display_df = reorder_df[['item_name', 'current_level', 'daily_usage', 'days_remaining', 'reorder_amount']].copy()
            display_df.columns = ['Item', 'Current Stock', 'Daily Usage', 'Days Remaining', 'Recommended Order']
            
            # Sort by days remaining
            display_df = display_df.sort_values('Days Remaining')
            
            # Add status color
            def status_color_rows(row):
                days = row['Days Remaining']
                color = get_status_color(days)
                return [f'background-color: {color}; opacity: 0.2' if col == 'Days Remaining' else '' for col in row.index]
            
            # Style the dataframe
            styled_df = display_df.style.apply(status_color_rows, axis=1)
            
            # Show dataframe
            st.dataframe(styled_df, use_container_width=True)
            
            # Create purchase order
            purchase_list = display_df[['Item', 'Recommended Order']].sort_values('Recommended Order', ascending=False)
            
            with st.expander("Generate Purchase Order"):
                st.markdown("#### Recommended Purchase Order")
                st.dataframe(purchase_list, use_container_width=True)
                
                # Download button for purchase order
                purchase_csv = purchase_list.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Purchase Order CSV",
                    data=purchase_csv,
                    file_name="purchase_order.csv",
                    mime="text/csv"
                )
        else:
            st.info("No items currently need reordering.")
        
        # Show day-by-day projection for a specific item
        st.markdown("#### Day-by-Day Inventory Projection")
        
        # Item selector
        selected_item = st.selectbox(
            "Select Item for Detailed Projection",
            options=df['item_name'].tolist(),
            index=0 if not df.empty else None
        )
        
        if selected_item:
            # Get the selected item data
            item_data = df[df['item_name'] == selected_item].iloc[0]
            day_by_day = item_data['day_by_day']
            
            # Convert to DataFrame
            daily_df = pd.DataFrame(day_by_day)
            daily_df['date'] = pd.to_datetime(daily_df['date'])
            daily_df['display_date'] = daily_df['date'].dt.strftime('%a, %b %d')
            
            # Define status colors
            status_colors = {
                'ok': '#2ecc71',      # Green
                'warning': '#f39c12',  # Orange
                'stockout': '#e74c3c'  # Red
            }
            
            # Create line and area chart
            fig = go.Figure()
            
            # Add area for remaining inventory
            fig.add_trace(go.Scatter(
                x=daily_df['display_date'],
                y=daily_df['remaining'],
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.3)',
                line=dict(color='rgba(52, 152, 219, 0.8)', width=2),
                name='Remaining Inventory'
            ))
            
            # Add line for usage
            fig.add_trace(go.Scatter(
                x=daily_df['display_date'],
                y=daily_df['projected_usage'],
                mode='lines+markers',
                line=dict(color='rgba(231, 76, 60, 0.8)', width=2, dash='dot'),
                name='Projected Usage'
            ))
            
            # Add title and labels
            fig.update_layout(
                title=f"Day-by-Day Projection for {selected_item}",
                xaxis_title="Date",
                yaxis_title="Quantity",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1a1a1a',
                height=400,
                margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # Display chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Show status calendar
            st.markdown("##### Inventory Status Calendar")
            
            # Prepare calendar data
            calendar_data = []
            for day in day_by_day:
                date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
                week_num = date_obj.isocalendar()[1] - datetime.now().isocalendar()[1] + 1
                weekday = date_obj.weekday()
                
                calendar_data.append({
                    'week': f"Week {week_num}",
                    'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][weekday],
                    'remaining': day['remaining'],
                    'status': day['status'],
                    'usage': day['projected_usage'],
                    'date': day['date']
                })
            
            calendar_df = pd.DataFrame(calendar_data)
            
            # Create heatmap
            fig = px.imshow(
                calendar_df.pivot(index='week', columns='day', values='remaining'),
                color_continuous_scale=[(0, "#e74c3c"), (0.3, "#f39c12"), (1, "#2ecc71")],
                labels=dict(x="Day", y="Week", color="Remaining"),
                text_auto='.1f',
                aspect="auto",
                height=250,
                title=f"Projected Inventory Calendar for {selected_item}"
            )
            
            # Ensure consistent day order
            day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            fig.update_xaxes(categoryorder='array', categoryarray=day_order)
            
            # Update layout
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1a1a1a',
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            # Display chart
            st.plotly_chart(fig, use_container_width=True)
