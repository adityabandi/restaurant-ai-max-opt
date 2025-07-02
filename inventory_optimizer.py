import pandas as pd
from typing import Dict, List, Optional

class InventoryOptimizer:
    def __init__(self):
        pass

    def generate_inventory_insights(self, sales_data: List[Dict], inventory_data: List[Dict]) -> List[Dict]:
        """Generate insights based on sales and inventory data"""
        insights = []
        
        try:
            # Create DataFrames
            sales_df = pd.DataFrame(sales_data)
            inventory_df = pd.DataFrame(inventory_data)
            
            # Skip if we don't have the necessary columns
            if 'item_name' not in sales_df.columns or 'quantity' not in sales_df.columns or \
               'item_name' not in inventory_df.columns or 'quantity' not in inventory_df.columns:
                return []
            
            # Get top selling items
            sales_summary = sales_df.groupby('item_name')['quantity'].sum().reset_index()
            sales_summary.columns = ['item_name', 'quantity_sold']
            
            # Add lowercase column for matching
            sales_summary['item_lower'] = sales_summary['item_name'].str.lower()
            inventory_df['item_lower'] = inventory_df['item_name'].str.lower()
            
            # Merge datasets
            merged = pd.merge(
                sales_summary,
                inventory_df,
                left_on='item_lower',
                right_on='item_lower',
                how='inner',
                suffixes=('_sales', '_inventory')
            )
            
            # Calculate days of inventory remaining
            if not merged.empty:
                # Assume sales data represents 30 days
                merged['daily_usage'] = merged['quantity_sold'] / 30
                merged['days_remaining'] = merged['quantity'] / merged['daily_usage']
                merged['days_remaining'] = merged['days_remaining'].fillna(99)  # Handle divide by zero
                merged['days_remaining'] = merged['days_remaining'].round(1)
                
                # Find items at risk of stockout
                stockout_risks = merged[merged['days_remaining'] < 7].sort_values('days_remaining')
                
                # Generate insights
                for _, row in stockout_risks.iterrows():
                    insights.append({
                        'type': 'inventory_alert',
                        'priority': 'high' if row['days_remaining'] < 3 else 'medium',
                        'title': f"⚠️ {row['item_name_sales']} Stockout Risk: {row['days_remaining']} Days Left",
                        'description': f"High-selling item with low inventory. Only {row['quantity']} units left with daily usage of {row['daily_usage']:.1f} units.",
                        'recommendation': f"Order {int(row['daily_usage'] * 14)} units to maintain 2-week supply",
                        'savings_potential': int(row['daily_usage'] * row['quantity_sold'] * 0.2),  # Estimated lost sales prevention
                        'confidence_score': 0.85,
                        'affected_items': [row['item_name_sales']]
                    })
                
                # Overstocked items
                overstocked = merged[merged['days_remaining'] > 60].sort_values('days_remaining', ascending=False)
                
                if not overstocked.empty:
                    insights.append({
                        'type': 'inventory_efficiency',
                        'priority': 'medium',
                        'title': f"💰 Overstocked Items: Capital Efficiency Opportunity",
                        'description': f"You have {len(overstocked)} items with over 60 days of inventory. This ties up unnecessary capital.",
                        'recommendation': "Reduce order quantities for these items to free up capital",
                        'savings_potential': int(sum(overstocked['quantity'] * 0.5 * overstocked['unit_cost']) if 'unit_cost' in overstocked.columns else 500),
                        'confidence_score': 0.8,
                        'affected_items': list(overstocked['item_name_sales'])
                    })
                
                # Overall inventory management insight
                if len(merged) > 5:  # Only if we have enough matching items
                    insights.append({
                        'type': 'inventory_management',
                        'priority': 'medium',
                        'title': f"🔄 Inventory-Sales Alignment Opportunity",
                        'description': f"Your inventory levels for top-selling items need adjustment based on sales velocity.",
                        'recommendation': "Implement automatic reorder points based on actual sales data",
                        'savings_potential': 1200,
                        'confidence_score': 0.82,
                        'action_items': [
                            "Set up weekly inventory-sales reconciliation",
                            "Create safety stock levels for top 10 items",
                            "Reduce order frequency for slow-moving items"
                        ]
                    })
        except Exception as e:
            print(f"Error generating sales-inventory insights: {str(e)}")
        
        return insights