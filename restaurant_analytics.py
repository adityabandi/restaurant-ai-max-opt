from data_warehouse import RestaurantDataWarehouse
from recipe_management import RecipeManagement
from predictive_analytics import PredictiveAnalytics
from typing import Dict, List, Optional, Any
import uuid
import json
from datetime import datetime

class RestaurantAnalytics:
    """Main integration class for restaurant analytics"""
    
    def __init__(self):
        self.data_warehouse = RestaurantDataWarehouse()
        self.recipe_manager = RecipeManagement()
        self.predictive_analytics = PredictiveAnalytics()
        self.initialized = False
        self.initialization_date = datetime.now()
    
    def process_uploaded_data(self, data: List[Dict], data_type: str, source_file: str = None) -> Dict:
        """Process uploaded data and distribute to appropriate systems
        
        Args:
            data: List of data dictionaries
            data_type: Type of data (sales, inventory, supplier, etc.)
            source_file: Original filename
            
        Returns:
            Dict with processing results
        """
        if not data:
            return {
                'success': False,
                'error': 'No data provided'
            }
        
        # Create a dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Add to data warehouse
        warehouse_result = self.data_warehouse.add_dataset(dataset_id, data_type, data, source_file)
        
        # Add to appropriate systems based on data type
        results = {
            'dataset_id': dataset_id,
            'data_type': data_type,
            'record_count': len(data),
            'source_file': source_file,
            'added_to_warehouse': warehouse_result,
            'added_to_recipe_system': False,
            'added_to_predictive_analytics': False
        }
        
        # Handle specific data types
        if data_type == 'sales':
            # Add to predictive analytics
            if 'date' in data[0]:
                prediction_result = self.predictive_analytics.add_historical_data('sales', data)
                results['added_to_predictive_analytics'] = prediction_result
        
        elif data_type == 'inventory':
            # Add to predictive analytics
            prediction_result = self.predictive_analytics.add_historical_data('inventory', data)
            results['added_to_predictive_analytics'] = prediction_result
        
        elif data_type == 'recipes':
            # Add to recipe management
            for recipe in data:
                if 'name' in recipe:
                    self.recipe_manager.add_recipe(recipe)
            results['added_to_recipe_system'] = True
        
        # Mark as initialized
        self.initialized = True
        
        return results
    
    def generate_insights(self) -> List[Dict]:
        """Generate comprehensive insights from all systems"""
        all_insights = []
        
        # Get cross-dataset insights from data warehouse
        if self.data_warehouse.get_dataset_count() > 0:
            warehouse_insights = self.data_warehouse.generate_cross_dataset_insights()
            all_insights.extend(warehouse_insights)
        
        # Get recipe insights if we have recipe data
        recipe_insights = self.recipe_manager.generate_recipe_insights()
        all_insights.extend(recipe_insights)
        
        # If we have both sales and recipe data, connect them
        sales_data = None
        for data_type in self.data_warehouse.get_all_data_types():
            if data_type == 'sales':
                sales_data = self.data_warehouse.get_combined_dataset('sales')
                break
        
        if sales_data:
            # Connect recipe data with sales data
            recipe_sales_insights = self.recipe_manager.connect_with_sales_data(sales_data)
            all_insights.extend(recipe_sales_insights)
            
            # Generate forecast insights
            forecast_insights = self.predictive_analytics.generate_forecast_insights()
            all_insights.extend(forecast_insights)
        
        # Sort insights by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_insights.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
        
        return all_insights
    
    def generate_sales_forecast(self, days_ahead: int = 14) -> Dict:
        """Generate sales forecast"""
        return self.predictive_analytics.generate_sales_forecast(days_ahead)
    
    def generate_inventory_forecast(self, days_ahead: int = 14) -> Dict:
        """Generate inventory forecast"""
        return self.predictive_analytics.generate_inventory_forecast(days_ahead)
    
    def add_recipe(self, recipe_data: Dict) -> str:
        """Add a recipe"""
        return self.recipe_manager.add_recipe(recipe_data)
    
    def get_data_relationships(self) -> Dict:
        """Get relationships between different datasets"""
        relationships = {}
        
        # Get all datasets from data warehouse
        for dataset_id in self.data_warehouse.metadata.keys():
            related = self.data_warehouse.get_related_datasets(dataset_id)
            if related:
                relationships[dataset_id] = related
        
        return relationships
    
    def get_system_status(self) -> Dict:
        """Get status information about all systems"""
        status = {
            'initialized': self.initialized,
            'initialization_date': self.initialization_date.isoformat(),
            'data_warehouse': {
                'dataset_count': self.data_warehouse.get_dataset_count(),
                'data_types': list(self.data_warehouse.get_all_data_types()),
                'relationship_count': len(self.data_warehouse.relationships)
            },
            'recipe_system': {
                'recipe_count': len(self.recipe_manager.recipes),
                'ingredient_count': len(self.recipe_manager.ingredients)
            },
            'predictive_analytics': {
                'forecast_count': len(self.predictive_analytics.forecasts),
                'has_sales_data': 'sales' in self.predictive_analytics.historical_data,
                'has_inventory_data': 'inventory' in self.predictive_analytics.historical_data
            }
        }
        
        return status
    
    def export_to_dict(self) -> Dict:
        """Export all data to a dictionary for serialization"""
        return {
            'initialization_date': self.initialization_date.isoformat(),
            'data_warehouse': self.data_warehouse.__dict__,
            'recipe_manager': self.recipe_manager.to_dict(),
            'predictive_analytics': self.predictive_analytics.to_dict()
        }
    
    def import_from_dict(self, data: Dict) -> bool:
        """Import data from a dictionary"""
        try:
            if 'initialization_date' in data:
                self.initialization_date = datetime.fromisoformat(data['initialization_date'])
            
            if 'data_warehouse' in data:
                self.data_warehouse.__dict__.update(data['data_warehouse'])
            
            if 'recipe_manager' in data:
                self.recipe_manager.from_dict(data['recipe_manager'])
            
            if 'predictive_analytics' in data:
                self.predictive_analytics.from_dict(data['predictive_analytics'])
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Error importing data: {str(e)}")
            return False
