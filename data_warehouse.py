import pandas as pd
import numpy as np

def get_sample_data() -> pd.DataFrame:
    """Load sample sales data from a demo CSV"""
    demo_file_path = 'demo-data/sample-sales-data.csv'
    return pd.read_csv(demo_file_path)

from typing import Dict, List, Set, Optional, Tuple, Any
from datetime import datetime
import json
from database import RestaurantDB

class RestaurantDataWarehouse:
    """Central data management system for restaurant analytics"""
    
    def __init__(self, db_path: str = 'restaurant_analytics.db'):
        self.db = RestaurantDB(db_path)
        self.relationships = {}
        self.last_updated = datetime.now()
        # Load existing datasets metadata from DB on init
        self.metadata = {ds['dataset_id']: ds for ds in self.db.get_all_datasets_metadata()}

    
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
            
        # Add/update dataset in the database
        success = self.db.add_dataset(dataset_id, data_type, data, source_file)
        if not success:
            return False

        # Update in-memory metadata after successful DB operation
        self.metadata[dataset_id] = {
            'data_type': data_type,
            'source_file': source_file,
            'row_count': len(data),
            'added_at': datetime.now(), # This will be updated by DB, but keep for consistency
            'columns': list(data[0].keys()) if data else [],
        }
        
        # Update relationships with other datasets
        self._update_relationships(dataset_id)
        
        self.last_updated = datetime.now()
        return True
    
    def get_dataset(self, dataset_id: str) -> Optional[List[Dict]]:
        """Retrieve a dataset by ID from the database"""
        dataset_record = self.db.get_dataset(dataset_id)
        return dataset_record['data'] if dataset_record else None
    
    def get_datasets_by_type(self, data_type: str) -> Dict[str, List[Dict]]:
        """Get all datasets of a specific type from the database"""
        dataset_records = self.db.get_datasets_by_type(data_type)
        return {ds['dataset_id']: ds['data'] for ds in dataset_records}
    
    def get_all_data_types(self) -> Set[str]:
        """Get all unique data types in the warehouse from the database"""
        return set(self.db.get_all_data_types())
    
    def get_dataset_count(self) -> int:
        """Get the count of datasets from the database"""
        return self.db.get_dataset_count()
    
    def get_combined_dataset(self, data_type: str) -> List[Dict]:
        """Combine all datasets of a specific type from the database"""
        return self.db.get_combined_dataset(data_type)
    
    def _update_relationships(self, new_dataset_id: str) -> None:
        """Detect and update relationships between datasets"""
        new_data_type = self.metadata[new_dataset_id]['data_type']
        new_data = self.get_dataset(new_dataset_id) # Retrieve data from DB
        
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
            existing_data = self.get_dataset(dataset_id) # Retrieve data from DB
            
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
                # Generate sales-inventory insights using the new InventoryOptimizer
                optimizer = InventoryOptimizer()
                sales_data = self.get_dataset(dataset_ids[0])
                inventory_data = self.get_dataset(dataset_ids[1])
                
                if sales_data and inventory_data:
                    sales_inventory_insights = optimizer.generate_inventory_insights(sales_data, inventory_data)
                    insights.extend(sales_inventory_insights)
        
        return insights
    
    def get_warehouse_stats(self) -> Dict:
        """Get statistics about the data warehouse"""
        stats = {
            'dataset_count': self.db.get_dataset_count(),
            'relationship_count': len(self.relationships),
            'data_types': list(self.get_all_data_types()),
            'total_records': sum(ds['row_count'] for ds in self.db.get_all_datasets_metadata()),
            'last_updated': self.last_updated.isoformat()
        }
        
        return stats
