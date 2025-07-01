import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import json

class PredictiveAnalytics:
    """Predictive analytics for restaurant sales forecasting"""
    
    def __init__(self):
        self.models = {}
        self.forecasts = {}
        self.last_updated = datetime.now()
        self.historical_data = {}
        self.seasonality_patterns = {}
        self.external_factors = []
    
    def add_historical_data(self, data_type: str, data: List[Dict], date_field: str = 'date') -> bool:
        """Add historical data for forecasting
        
        Args:
            data_type: Type of data (sales, inventory, etc.)
            data: The actual data as a list of dictionaries
            date_field: Name of the date field in the data
            
        Returns:
            bool: True if successful
        """
        if not data:
            return False
        
        # Check if date field exists in the data
        if date_field not in data[0]:
            return False
        
        # Store the data
        self.historical_data[data_type] = data
        
        # Extract and store seasonality patterns
        self._extract_seasonality_patterns(data_type, data, date_field)
        
        self.last_updated = datetime.now()
        return True
    
    def _extract_seasonality_patterns(self, data_type: str, data: List[Dict], date_field: str) -> None:
        """Extract seasonality patterns from historical data"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Make sure date is a datetime
            df[date_field] = pd.to_datetime(df[date_field])
            
            # Extract date components
            df['day_of_week'] = df[date_field].dt.dayofweek  # 0=Monday, 6=Sunday
            df['month'] = df[date_field].dt.month
            df['week_of_year'] = df[date_field].dt.isocalendar().week
            df['is_weekend'] = df['day_of_week'].isin([5, 6])  # Saturday and Sunday
            
            # Extract patterns for different data types
            if data_type == 'sales':
                if 'total_amount' in df.columns:
                    # Daily patterns
                    daily_pattern = df.groupby('day_of_week')['total_amount'].mean().to_dict()
                    
                    # Monthly patterns
                    monthly_pattern = df.groupby('month')['total_amount'].mean().to_dict()
                    
                    # Weekend vs weekday
                    weekend_pattern = df.groupby('is_weekend')['total_amount'].mean().to_dict()
                    
                    self.seasonality_patterns[data_type] = {
                        'daily': daily_pattern,
                        'monthly': monthly_pattern,
                        'weekend_vs_weekday': weekend_pattern
                    }
            
            elif data_type == 'inventory':
                # Inventory patterns would be different
                pass
        
        except Exception as e:
            print(f"Error extracting seasonality patterns: {str(e)}")
    
    def add_external_factor(self, factor: Dict) -> None:
        """Add external factor like holidays, events, weather forecasts
        
        Args:
            factor: Dict with factor details including date, type, and impact_multiplier
        """
        if 'date' not in factor or 'type' not in factor or 'impact_multiplier' not in factor:
            return
        
        # Add to external factors list
        self.external_factors.append({
            'date': factor['date'],
            'type': factor['type'],
            'description': factor.get('description', ''),
            'impact_multiplier': float(factor['impact_multiplier']),
            'added_at': datetime.now().isoformat()
        })
    
    def generate_sales_forecast(self, days_ahead: int = 14) -> Dict:
        """Generate sales forecast for the next N days
        
        Args:
            days_ahead: Number of days to forecast
            
        Returns:
            Dict with forecast details
        """
        if 'sales' not in self.historical_data:
            return {
                'success': False,
                'error': 'No historical sales data available for forecasting'
            }
        
        try:
            sales_data = self.historical_data['sales']
            
            # Convert to DataFrame
            df = pd.DataFrame(sales_data)
            
            # Make sure we have the required columns
            if 'date' not in df.columns or 'total_amount' not in df.columns:
                return {
                    'success': False,
                    'error': 'Missing required columns (date, total_amount) in sales data'
                }
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by date
            daily_sales = df.groupby('date')['total_amount'].sum().reset_index()
            
            # Sort by date
            daily_sales = daily_sales.sort_values('date')
            
            # Generate forecasts using different methods
            # Here we're using a simple average + seasonality model
            # In a real system, you'd use more sophisticated models like ARIMA, Prophet, etc.
            
            # Calculate average daily sales from last 30 days
            last_30_days = daily_sales.iloc[-30:]
            average_daily_sales = last_30_days['total_amount'].mean()
            
            # Generate dates for forecast
            last_date = daily_sales['date'].max()
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            
            # Prepare forecast
            forecast = []
            for forecast_date in forecast_dates:
                # Get day of week
                day_of_week = forecast_date.dayofweek
                month = forecast_date.month
                is_weekend = day_of_week in [5, 6]  # Saturday and Sunday
                
                # Apply seasonality factors
                seasonality_factors = self.seasonality_patterns.get('sales', {})
                
                daily_factor = 1.0
                if 'daily' in seasonality_factors and day_of_week in seasonality_factors['daily']:
                    daily_avg = sum(seasonality_factors['daily'].values()) / len(seasonality_factors['daily'])
                    daily_factor = seasonality_factors['daily'][day_of_week] / daily_avg if daily_avg > 0 else 1.0
                
                monthly_factor = 1.0
                if 'monthly' in seasonality_factors and month in seasonality_factors['monthly']:
                    monthly_avg = sum(seasonality_factors['monthly'].values()) / len(seasonality_factors['monthly'])
                    monthly_factor = seasonality_factors['monthly'][month] / monthly_avg if monthly_avg > 0 else 1.0
                
                weekend_factor = 1.0
                if 'weekend_vs_weekday' in seasonality_factors and int(is_weekend) in seasonality_factors['weekend_vs_weekday']:
                    weekend_map = seasonality_factors['weekend_vs_weekday']
                    weekend_avg = sum(weekend_map.values()) / len(weekend_map)
                    weekend_factor = weekend_map[int(is_weekend)] / weekend_avg if weekend_avg > 0 else 1.0
                
                # Calculate combined factor
                combined_factor = daily_factor * monthly_factor * weekend_factor
                
                # Apply external factors
                external_factor = 1.0
                for factor in self.external_factors:
                    factor_date = pd.to_datetime(factor['date']).date()
                    if factor_date == forecast_date.date():
                        external_factor *= factor['impact_multiplier']
                
                # Calculate forecasted amount
                forecasted_amount = average_daily_sales * combined_factor * external_factor
                
                # Add to forecast
                forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'forecasted_amount': round(forecasted_amount, 2),
                    'factors': {
                        'daily': round(daily_factor, 2),
                        'monthly': round(monthly_factor, 2),
                        'weekend': round(weekend_factor, 2),
                        'external': round(external_factor, 2),
                        'combined': round(combined_factor * external_factor, 2)
                    }
                })
            
            # Store the forecast
            forecast_id = f"sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.forecasts[forecast_id] = {
                'type': 'sales',
                'generated_at': datetime.now().isoformat(),
                'days_ahead': days_ahead,
                'forecast': forecast
            }
            
            return {
                'success': True,
                'forecast_id': forecast_id,
                'forecast': forecast
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating forecast: {str(e)}"
            }
    
    def generate_inventory_forecast(self, days_ahead: int = 14) -> Dict:
        """Generate inventory forecast based on sales forecast
        
        Args:
            days_ahead: Number of days to forecast
            
        Returns:
            Dict with forecast details
        """
        # First, generate a sales forecast
        sales_forecast_result = self.generate_sales_forecast(days_ahead)
        
        if not sales_forecast_result['success']:
            return sales_forecast_result
        
        # Get the sales forecast
        sales_forecast = sales_forecast_result['forecast']
        
        # Check if we have inventory data
        if 'inventory' not in self.historical_data:
            return {
                'success': False,
                'error': 'No historical inventory data available for forecasting'
            }
        
        try:
            inventory_data = self.historical_data['inventory']
            
            # Convert to DataFrame
            inventory_df = pd.DataFrame(inventory_data)
            
            # Check if we have sales data with item-level detail
            if 'sales' not in self.historical_data:
                return {
                    'success': False,
                    'error': 'No historical sales data available for item-level forecasting'
                }
            
            sales_data = self.historical_data['sales']
            sales_df = pd.DataFrame(sales_data)
            
            # Make sure we have required columns
            if 'item_name' not in sales_df.columns or 'quantity' not in sales_df.columns or 'date' not in sales_df.columns:
                return {
                    'success': False,
                    'error': 'Missing required columns in sales data for inventory forecasting'
                }
            
            if 'item_name' not in inventory_df.columns or 'quantity' not in inventory_df.columns:
                return {
                    'success': False,
                    'error': 'Missing required columns in inventory data for forecasting'
                }
            
            # Convert date to datetime
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            
            # Calculate average daily usage by item
            last_30_days_sales = sales_df[sales_df['date'] >= (pd.to_datetime('today') - pd.Timedelta(days=30))]
            daily_usage_by_item = last_30_days_sales.groupby('item_name')['quantity'].sum() / 30
            
            # Get current inventory levels
            current_inventory = inventory_df.set_index('item_name')['quantity']
            
            # Calculate days of inventory remaining
            inventory_forecast = []
            
            for item_name in current_inventory.index:
                if item_name in daily_usage_by_item.index:
                    current_level = current_inventory[item_name]
                    daily_usage = daily_usage_by_item[item_name]
                    
                    # Calculate days remaining
                    if daily_usage > 0:
                        days_remaining = current_level / daily_usage
                    else:
                        days_remaining = 99  # Arbitrary high value
                    
                    # Generate day-by-day forecast
                    item_forecast = []
                    remaining = current_level
                    
                    for i, forecast_day in enumerate(sales_forecast):
                        forecast_date = forecast_day['date']
                        sales_factor = forecast_day['factors']['combined']
                        
                        # Adjust usage by sales factor
                        adjusted_usage = daily_usage * sales_factor
                        
                        # Update remaining inventory
                        remaining -= adjusted_usage
                        remaining = max(0, remaining)  # Can't go below zero
                        
                        # Add to item forecast
                        item_forecast.append({
                            'date': forecast_date,
                            'projected_usage': round(adjusted_usage, 2),
                            'remaining': round(remaining, 2),
                            'status': 'ok' if remaining > (daily_usage * 3) else 'warning' if remaining > 0 else 'stockout'
                        })
                    
                    # Add item forecast to main forecast
                    inventory_forecast.append({
                        'item_name': item_name,
                        'current_level': current_level,
                        'daily_usage': daily_usage,
                        'days_remaining': round(days_remaining, 1),
                        'reorder_needed': days_remaining < 14,  # Flag if less than 2 weeks
                        'reorder_amount': round(daily_usage * 30) if days_remaining < 14 else 0,  # 30-day supply
                        'day_by_day': item_forecast
                    })
            
            # Sort by days remaining
            inventory_forecast.sort(key=lambda x: x['days_remaining'])
            
            # Store the forecast
            forecast_id = f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.forecasts[forecast_id] = {
                'type': 'inventory',
                'generated_at': datetime.now().isoformat(),
                'days_ahead': days_ahead,
                'forecast': inventory_forecast
            }
            
            return {
                'success': True,
                'forecast_id': forecast_id,
                'forecast': inventory_forecast
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating inventory forecast: {str(e)}"
            }
    
    def get_forecast(self, forecast_id: str) -> Optional[Dict]:
        """Get a previously generated forecast"""
        return self.forecasts.get(forecast_id)
    
    def get_latest_forecast(self, forecast_type: str) -> Optional[Dict]:
        """Get the most recent forecast of a specific type"""
        # Filter forecasts by type
        type_forecasts = [f for f_id, f in self.forecasts.items() if f['type'] == forecast_type]
        
        if not type_forecasts:
            return None
        
        # Sort by generation time
        sorted_forecasts = sorted(type_forecasts, key=lambda x: x['generated_at'], reverse=True)
        
        return sorted_forecasts[0] if sorted_forecasts else None
    
    def generate_forecast_insights(self) -> List[Dict]:
        """Generate insights based on forecasts"""
        insights = []
        
        # Get latest forecasts
        sales_forecast = self.get_latest_forecast('sales')
        inventory_forecast = self.get_latest_forecast('inventory')
        
        # Generate sales forecast insights
        if sales_forecast:
            forecast_data = sales_forecast['forecast']
            
            # Identify peaks and valleys
            if len(forecast_data) >= 7:  # At least a week of data
                daily_amounts = [day['forecasted_amount'] for day in forecast_data]
                avg_amount = sum(daily_amounts) / len(daily_amounts)
                
                # Find peak days
                peak_days = []
                for day in forecast_data:
                    if day['forecasted_amount'] > avg_amount * 1.15:  # 15% above average
                        peak_days.append(day)
                
                if peak_days:
                    peak_days = sorted(peak_days, key=lambda x: x['forecasted_amount'], reverse=True)[:3]  # Top 3
                    
                    insights.append({
                        'type': 'peak_sales_forecast',
                        'priority': 'medium',
                        'title': f"ud83dudcc8 Peak Sales Days Approaching",
                        'description': f"Forecasting {len(peak_days)} high-volume days in the next 2 weeks",
                        'recommendation': f"Increase staffing on {peak_days[0]['date']} - forecasting ${peak_days[0]['forecasted_amount']:,.2f} in sales",
                        'savings_potential': int(sum(day['forecasted_amount'] * 0.05 for day in peak_days)),  # 5% optimization
                        'confidence_score': 0.8,
                        'action_items': [
                            f"Schedule extra staff on {day['date']} (${day['forecasted_amount']:,.0f} projected)" 
                            for day in peak_days
                        ]
                    })
        
        # Generate inventory forecast insights
        if inventory_forecast:
            forecast_data = inventory_forecast['forecast']
            
            # Identify potential stockouts
            stockout_risks = []
            for item in forecast_data:
                if item['days_remaining'] < 7:  # Less than a week
                    stockout_risks.append(item)
            
            if stockout_risks:
                insights.append({
                    'type': 'inventory_stockout_risk',
                    'priority': 'high',
                    'title': f"u26a0ufe0f Projected Stockout Risk for {len(stockout_risks)} Items",
                    'description': f"Based on sales forecast, you'll run out of {stockout_risks[0]['item_name']} in {stockout_risks[0]['days_remaining']} days",
                    'recommendation': f"Place orders immediately for at-risk items",
                    'savings_potential': int(sum(item['daily_usage'] * item['days_remaining'] * 20 for item in stockout_risks)),  # Estimate of lost sales
                    'confidence_score': 0.85,
                    'action_items': [
                        f"Order {item['reorder_amount']} units of {item['item_name']} (only {item['days_remaining']} days left)" 
                        for item in stockout_risks[:3]  # Top 3 most urgent
                    ]
                })
        
        return insights
    
    def to_dict(self) -> Dict:
        """Export predictive analytics data to dict for serialization"""
        return {
            'forecasts': self.forecasts,
            'seasonality_patterns': self.seasonality_patterns,
            'external_factors': self.external_factors,
            'last_updated': self.last_updated.isoformat()
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load predictive analytics data from dict"""
        self.forecasts = data.get('forecasts', {})
        self.seasonality_patterns = data.get('seasonality_patterns', {})
        self.external_factors = data.get('external_factors', [])
        self.last_updated = datetime.now()
