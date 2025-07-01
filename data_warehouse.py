import pandas as pd
import numpy as np
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
import json

class RestaurantDataWarehouse:
    """Central data management system for restaurant analytics"""
    
    def __init__(self):
        self.datasets = {}
        self.relationships = {}
        self.metadata = {}
        self.last_updated = datetime.now()
    
    def add_dataset(self, dataset_id: str, data_type: str, data: List[Dict], source_file: str = None) -> bool:
        """Add a new dataset to the warehouse
        
        Args:
            dataset_id: Unique identifier for the dataset
            data_type: Type of data (sales, inventory, etc.)
            data: The actual data as a list of dictionaries
            source_file: Original filename (optional)
            
        Returns:
            bool: True if successful
        """
        if not data:
            return False
            
        # Store the dataset with metadata
        self.datasets[dataset_id] = data
        
        # Store metadata
        self.metadata[dataset_id] = {
            'data_type': data_type,
            'source_file': source_file,
            'row_count': len(data),
            'added_at': datetime.now(),
            'columns': list(data[0].keys()) if data else [],
        }
        
        # Update relationships with other datasets
        self._update_relationships(dataset_id)
        
        self.last_updated = datetime.now()
        return True
    
    def get_dataset(self, dataset_id: str) -> Optional[List[Dict]]:
        """Retrieve a dataset by ID"""
        return self.datasets.get(dataset_id)
    
    def get_datasets_by_type(self, data_type: str) -> Dict[str, List[Dict]]:
        """Get all datasets of a specific type"""
        result = {}
        for dataset_id, metadata in self.metadata.items():
            if metadata['data_type'] == data_type:
                result[dataset_id] = self.datasets[dataset_id]
        return result
    
    def get_all_data_types(self) -> Set[str]:
        """Get all unique data types in the warehouse"""
        return {metadata['data_type'] for metadata in self.metadata.values()}
    
    def get_dataset_count(self) -> int:
        """Get the count of datasets"""
        return len(self.datasets)
    
    def get_combined_dataset(self, data_type: str) -> List[Dict]:
        """Combine all datasets of a specific type"""
        combined = []
        for dataset_id, metadata in self.metadata.items():
            if metadata['data_type'] == data_type:
                combined.extend(self.datasets[dataset_id])
        return combined
    
    def _update_relationships(self, new_dataset_id: str) -> None:
        """Detect and update relationships between datasets"""
        new_data_type = self.metadata[new_dataset_id]['data_type']
        new_data = self.datasets[new_dataset_id]
        
        # Define relationship rules
        relationship_rules = {
            ('sales', 'inventory'): self._detect_sales_inventory_relationship,
            ('sales', 'supplier'): self._detect_sales_supplier_relationship,
            ('inventory', 'supplier'): self._detect_inventory_supplier_relationship,
            ('sales', 'recipes'): self._detect_sales_recipe_relationship,
        }
        
        # Check for relationships with existing datasets
        for dataset_id, metadata in self.metadata.items():
            if dataset_id == new_dataset_id:
                continue
                
            existing_data_type = metadata['data_type']
            existing_data = self.datasets[dataset_id]
            
            # Check if we have a rule for this combination
            rule_key = (new_data_type, existing_data_type)
            reverse_rule_key = (existing_data_type, new_data_type)
            
            if rule_key in relationship_rules:
                relationship = relationship_rules[rule_key](new_data, existing_data)
                if relationship:
                    self.relationships[f"{new_dataset_id}-{dataset_id}"] = relationship
            elif reverse_rule_key in relationship_rules:
                relationship = relationship_rules[reverse_rule_key](existing_data, new_data)
                if relationship:
                    self.relationships[f"{dataset_id}-{new_dataset_id}"] = relationship
    
    def _detect_sales_inventory_relationship(self, sales_data: List[Dict], inventory_data: List[Dict]) -> Optional[Dict]:
        """Detect relationships between sales and inventory data"""
        # Extract item names from both datasets
        sales_items = set()
        for item in sales_data:
            if 'item_name' in item and item['item_name']:
                sales_items.add(item['item_name'].lower())
        
        inventory_items = set()
        for item in inventory_data:
            if 'item_name' in item and item['item_name']:
                inventory_items.add(item['item_name'].lower())
        
        # Find common items
        common_items = sales_items.intersection(inventory_items)
        
        if common_items:
            return {
                'type': 'sales_inventory',
                'strength': len(common_items) / max(len(sales_items), len(inventory_items)),
                'common_items': list(common_items),
                'common_item_count': len(common_items),
                'relationship_description': 'Sales and inventory data share item names'
            }
        return None
    
    def _detect_sales_supplier_relationship(self, sales_data: List[Dict], supplier_data: List[Dict]) -> Optional[Dict]:
        """Detect relationships between sales and supplier data"""
        # This is a placeholder - in a real system we would implement more sophisticated detection
        return {
            'type': 'sales_supplier',
            'strength': 0.5,  # Placeholder value
            'relationship_description': 'Sales and supplier data may be related through items'
        }
    
    def _detect_inventory_supplier_relationship(self, inventory_data: List[Dict], supplier_data: List[Dict]) -> Optional[Dict]:
        """Detect relationships between inventory and supplier data"""
        # This is a placeholder - in a real system we would implement more sophisticated detection
        return {
            'type': 'inventory_supplier',
            'strength': 0.6,  # Placeholder value
            'relationship_description': 'Inventory and supplier data may be related through items'
        }
    
    def _detect_sales_recipe_relationship(self, sales_data: List[Dict], recipe_data: List[Dict]) -> Optional[Dict]:
        """Detect relationships between sales and recipe data"""
        # This is a placeholder since we don't have recipe data yet
        return None
    
    def get_related_datasets(self, dataset_id: str) -> Dict[str, Dict]:
        """Get all datasets that are related to the given dataset"""
        related = {}
        
        for rel_key, rel_data in self.relationships.items():
            ids = rel_key.split('-')
            if dataset_id in ids:
                other_id = ids[0] if ids[1] == dataset_id else ids[1]
                related[other_id] = {
                    'relationship': rel_data,
                    'metadata': self.metadata[other_id]
                }
        
        return related
    
    def generate_cross_dataset_insights(self) -> List[Dict]:
        """Generate insights by analyzing multiple datasets together"""
        insights = []
        
        # Generate insights for each relationship type
        for rel_key, rel_data in self.relationships.items():
            dataset_ids = rel_key.split('-')
            
            if rel_data['type'] == 'sales_inventory':
                # Generate sales-inventory insights
                sales_inventory_insights = self._generate_sales_inventory_insights(
                    self.datasets[dataset_ids[0]],
                    self.datasets[dataset_ids[1]],
                    rel_data
                )
                insights.extend(sales_inventory_insights)
        
        return insights
    
    def _generate_sales_inventory_insights(self, sales_data: List[Dict], inventory_data: List[Dict], 
                                          relationship: Dict) -> List[Dict]:
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
    
    def get_warehouse_stats(self) -> Dict:
        """Get statistics about the data warehouse"""
        stats = {
            'dataset_count': len(self.datasets),
            'relationship_count': len(self.relationships),
            'data_types': list(self.get_all_data_types()),
            'total_records': sum(len(data) for data in self.datasets.values()),
            'last_updated': self.last_updated.isoformat()
        }
        
        return stats
