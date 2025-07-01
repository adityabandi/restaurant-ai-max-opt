import pandas as pd
from typing import Dict, List, Optional, Tuple, Set
import uuid
import json
from datetime import datetime

class RecipeManagement:
    """Recipe cost analysis and management system"""
    
    def __init__(self):
        self.recipes = {}
        self.ingredients = {}
        self.ingredient_prices = {}
        self.recipe_metrics = {}
        self.last_updated = datetime.now()
    
    def add_recipe(self, recipe_data: Dict) -> str:
        """Add a new recipe to the system
        
        Args:
            recipe_data: Recipe data including name, ingredients, and optional cost data
            
        Returns:
            str: Recipe ID
        """
        if 'name' not in recipe_data or not recipe_data['name']:
            raise ValueError("Recipe must have a name")
            
        recipe_id = str(uuid.uuid4())
        
        # Store the recipe
        self.recipes[recipe_id] = {
            'id': recipe_id,
            'name': recipe_data['name'],
            'ingredients': recipe_data.get('ingredients', []),
            'instructions': recipe_data.get('instructions', ''),
            'category': recipe_data.get('category', 'Uncategorized'),
            'portion_size': recipe_data.get('portion_size', 1),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add any ingredients to the master list
        for ingredient in recipe_data.get('ingredients', []):
            if 'name' in ingredient and ingredient['name']:
                self._add_or_update_ingredient(ingredient)
        
        # Calculate and store metrics
        self._calculate_recipe_metrics(recipe_id)
        
        self.last_updated = datetime.now()
        return recipe_id
    
    def _add_or_update_ingredient(self, ingredient_data: Dict) -> str:
        """Add or update an ingredient in the master list"""
        ingredient_name = ingredient_data['name'].lower()
        
        # Generate a stable ID based on the name
        ingredient_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, ingredient_name))
        
        if ingredient_id not in self.ingredients:
            self.ingredients[ingredient_id] = {
                'id': ingredient_id,
                'name': ingredient_data['name'],
                'unit': ingredient_data.get('unit', 'each'),
                'category': ingredient_data.get('category', 'Uncategorized'),
                'created_at': datetime.now().isoformat()
            }
        
        # Update ingredient price if provided
        if 'unit_price' in ingredient_data and ingredient_data['unit_price'] is not None:
            self.ingredient_prices[ingredient_id] = {
                'price': float(ingredient_data['unit_price']),
                'updated_at': datetime.now().isoformat()
            }
        
        return ingredient_id
    
    def _calculate_recipe_metrics(self, recipe_id: str) -> None:
        """Calculate cost metrics for a recipe"""
        if recipe_id not in self.recipes:
            return
            
        recipe = self.recipes[recipe_id]
        
        # Initialize metrics
        metrics = {
            'total_cost': 0.0,
            'ingredient_count': len(recipe['ingredients']),
            'missing_prices': [],
            'price_coverage': 0.0,
            'estimated': True,
            'labor_cost_estimate': 0.0,
            'overhead_estimate': 0.0,
            'calculated_at': datetime.now().isoformat()
        }
        
        # Calculate total ingredient cost
        ingredients_with_prices = 0
        for ingredient in recipe['ingredients']:
            ingredient_name = ingredient.get('name', '').lower()
            if not ingredient_name:
                continue
                
            # Find ingredient ID
            ingredient_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, ingredient_name))
            
            # Get quantity
            quantity = float(ingredient.get('quantity', 1))
            
            # Check if we have a price
            if ingredient_id in self.ingredient_prices:
                price_data = self.ingredient_prices[ingredient_id]
                ingredient_cost = quantity * price_data['price']
                metrics['total_cost'] += ingredient_cost
                ingredients_with_prices += 1
            else:
                metrics['missing_prices'].append(ingredient_name)
        
        # Calculate price coverage
        if recipe['ingredients']:
            metrics['price_coverage'] = ingredients_with_prices / len(recipe['ingredients'])
        
        # Estimate labor cost based on complexity (this is a placeholder implementation)
        instruction_length = len(recipe.get('instructions', ''))
        ingredient_count = len(recipe['ingredients'])
        
        # Simple complexity heuristic
        complexity_factor = 0.5
        if instruction_length > 500:
            complexity_factor = 1.0
        elif instruction_length > 200:
            complexity_factor = 0.7
            
        if ingredient_count > 10:
            complexity_factor += 0.3
        elif ingredient_count > 5:
            complexity_factor += 0.1
            
        # Estimate labor cost - assume $15/hour and convert to minutes
        labor_minutes = 5 + (ingredient_count * 2) + (instruction_length / 50)
        metrics['labor_minutes'] = labor_minutes
        metrics['labor_cost_estimate'] = (labor_minutes / 60) * 15 * complexity_factor
        
        # Estimate overhead (30% of ingredient cost)
        metrics['overhead_estimate'] = metrics['total_cost'] * 0.3
        
        # Calculate total cost
        metrics['full_cost'] = metrics['total_cost'] + metrics['labor_cost_estimate'] + metrics['overhead_estimate']
        
        # Calculate cost per portion
        metrics['cost_per_portion'] = metrics['full_cost'] / max(1, recipe.get('portion_size', 1))
        
        # Store metrics
        self.recipe_metrics[recipe_id] = metrics
    
    def update_recipe(self, recipe_id: str, recipe_data: Dict) -> bool:
        """Update an existing recipe"""
        if recipe_id not in self.recipes:
            return False
            
        # Update recipe fields
        current_recipe = self.recipes[recipe_id]
        for key, value in recipe_data.items():
            if key in ['name', 'ingredients', 'instructions', 'category', 'portion_size']:
                current_recipe[key] = value
        
        current_recipe['updated_at'] = datetime.now().isoformat()
        
        # Update ingredients
        for ingredient in current_recipe.get('ingredients', []):
            if 'name' in ingredient and ingredient['name']:
                self._add_or_update_ingredient(ingredient)
        
        # Recalculate metrics
        self._calculate_recipe_metrics(recipe_id)
        
        self.last_updated = datetime.now()
        return True
    
    def update_ingredient_price(self, ingredient_name: str, price: float) -> bool:
        """Update price for an ingredient"""
        ingredient_name = ingredient_name.lower()
        ingredient_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, ingredient_name))
        
        # Create ingredient if it doesn't exist
        if ingredient_id not in self.ingredients:
            self._add_or_update_ingredient({
                'name': ingredient_name,
                'unit_price': price
            })
            return True
        
        # Update price
        self.ingredient_prices[ingredient_id] = {
            'price': float(price),
            'updated_at': datetime.now().isoformat()
        }
        
        # Recalculate all recipes using this ingredient
        for recipe_id, recipe in self.recipes.items():
            for ingredient in recipe.get('ingredients', []):
                if ingredient.get('name', '').lower() == ingredient_name:
                    self._calculate_recipe_metrics(recipe_id)
                    break
        
        self.last_updated = datetime.now()
        return True
    
    def get_recipe(self, recipe_id: str) -> Optional[Dict]:
        """Get recipe by ID with its metrics"""
        if recipe_id not in self.recipes:
            return None
            
        recipe = self.recipes[recipe_id].copy()
        
        # Add metrics if available
        if recipe_id in self.recipe_metrics:
            recipe['metrics'] = self.recipe_metrics[recipe_id]
        
        return recipe
    
    def get_all_recipes(self) -> List[Dict]:
        """Get all recipes with their metrics"""
        result = []
        
        for recipe_id, recipe in self.recipes.items():
            recipe_copy = recipe.copy()
            
            # Add metrics if available
            if recipe_id in self.recipe_metrics:
                recipe_copy['metrics'] = self.recipe_metrics[recipe_id]
            
            result.append(recipe_copy)
        
        return result
    
    def get_ingredient_list(self) -> List[Dict]:
        """Get list of all ingredients with prices"""
        result = []
        
        for ingredient_id, ingredient in self.ingredients.items():
            ingredient_copy = ingredient.copy()
            
            # Add price if available
            if ingredient_id in self.ingredient_prices:
                ingredient_copy['price'] = self.ingredient_prices[ingredient_id]['price']
                ingredient_copy['price_updated_at'] = self.ingredient_prices[ingredient_id]['updated_at']
            
            result.append(ingredient_copy)
        
        return result
    
    def generate_recipe_insights(self) -> List[Dict]:
        """Generate insights about recipes and costs"""
        insights = []
        
        if not self.recipes or not self.recipe_metrics:
            return [{
                'type': 'recipe_data_missing',
                'priority': 'low',
                'title': 'Add Recipe Data to Unlock Cost Insights',
                'description': 'Upload or enter your recipe data to get detailed cost analysis and optimization suggestions.',
                'recommendation': 'Import recipes from your POS system or enter them manually',
                'confidence_score': 0.9
            }]
        
        # Identify high-cost recipes
        high_cost_recipes = []
        for recipe_id, metrics in self.recipe_metrics.items():
            if metrics['cost_per_portion'] > 10.0:  # This threshold would be adjusted based on restaurant type
                high_cost_recipes.append((recipe_id, self.recipes[recipe_id]['name'], metrics['cost_per_portion']))
        
        if high_cost_recipes:
            high_cost_recipes.sort(key=lambda x: x[2], reverse=True)
            top_high_cost = high_cost_recipes[:3]
            
            insights.append({
                'type': 'recipe_cost_optimization',
                'priority': 'high',
                'title': f"💰 High Food Cost Items Identified",
                'description': f"Found {len(high_cost_recipes)} recipes with high food costs, including {top_high_cost[0][1]} at ${top_high_cost[0][2]:.2f} per portion",
                'recommendation': "Review these recipes to reduce ingredient costs or increase menu prices",
                'savings_potential': int(sum(cost * 5 for _, _, cost in top_high_cost)),  # Estimate savings
                'confidence_score': 0.85,
                'affected_items': [name for _, name, _ in top_high_cost]
            })
        
        # Identify recipes with missing ingredient prices
        incomplete_recipes = []
        for recipe_id, metrics in self.recipe_metrics.items():
            if metrics['missing_prices'] and metrics['price_coverage'] < 0.8:
                incomplete_recipes.append((recipe_id, self.recipes[recipe_id]['name'], len(metrics['missing_prices'])))
        
        if incomplete_recipes:
            incomplete_recipes.sort(key=lambda x: x[2], reverse=True)
            
            insights.append({
                'type': 'incomplete_recipe_data',
                'priority': 'medium',
                'title': f"⚠️ Incomplete Recipe Cost Data",
                'description': f"Found {len(incomplete_recipes)} recipes with missing ingredient prices",
                'recommendation': "Update missing ingredient prices for accurate cost analysis",
                'confidence_score': 0.9,
                'affected_items': [name for _, name, _ in incomplete_recipes[:5]]
            })
        
        # For future: Add insights about recipe popularity vs. profitability
        # This would require integration with sales data
        
        return insights
    
    def connect_with_sales_data(self, sales_data: List[Dict]) -> List[Dict]:
        """Connect recipe data with sales data to generate profitability insights"""
        insights = []
        
        if not self.recipes or not sales_data:
            return insights
        
        # Create a map of recipe names to IDs for easy lookup
        recipe_name_to_id = {recipe['name'].lower(): recipe_id for recipe_id, recipe in self.recipes.items()}
        
        # Create a DataFrame from sales data
        try:
            sales_df = pd.DataFrame(sales_data)
            
            if 'item_name' not in sales_df.columns or 'price' not in sales_df.columns:
                return insights
            
            # Aggregate sales by item
            sales_summary = sales_df.groupby('item_name').agg({
                'quantity': 'sum',
                'price': 'mean',
                'total_amount': 'sum'
            }).reset_index()
            
            # Match sales data with recipes
            profitable_items = []
            unprofitable_items = []
            
            for _, row in sales_summary.iterrows():
                item_name = row['item_name'].lower()
                
                # Check if this item has a recipe
                if item_name in recipe_name_to_id:
                    recipe_id = recipe_name_to_id[item_name]
                    
                    if recipe_id in self.recipe_metrics:
                        metrics = self.recipe_metrics[recipe_id]
                        
                        # Calculate profitability
                        cost = metrics['cost_per_portion']
                        price = row['price']
                        margin = price - cost
                        margin_percent = (margin / price) * 100 if price > 0 else 0
                        
                        if margin_percent < 20:  # Less than 20% margin is concerning
                            unprofitable_items.append({
                                'name': row['item_name'],
                                'cost': cost,
                                'price': price,
                                'margin': margin,
                                'margin_percent': margin_percent,
                                'quantity_sold': row['quantity'],
                                'total_revenue': row['total_amount']
                            })
                        elif margin_percent > 70:  # Extremely profitable
                            profitable_items.append({
                                'name': row['item_name'],
                                'cost': cost,
                                'price': price,
                                'margin': margin,
                                'margin_percent': margin_percent,
                                'quantity_sold': row['quantity'],
                                'total_revenue': row['total_amount']
                            })
            
            # Generate insights for unprofitable items
            if unprofitable_items:
                # Sort by margin percent (ascending)
                unprofitable_items.sort(key=lambda x: x['margin_percent'])
                
                total_impact = sum(item['quantity_sold'] * (item['price'] * 0.1) for item in unprofitable_items[:3])
                
                insights.append({
                    'type': 'menu_profitability',
                    'priority': 'high',
                    'title': f"❗ Low Margin Menu Items Identified",
                    'description': f"Found {len(unprofitable_items)} menu items with margins below 20%, including {unprofitable_items[0]['name']} at only {unprofitable_items[0]['margin_percent']:.1f}% margin",
                    'recommendation': f"Increase prices or reduce costs for these items to improve profitability",
                    'savings_potential': int(total_impact),
                    'confidence_score': 0.9,
                    'affected_items': [item['name'] for item in unprofitable_items[:3]],
                    'action_items': [
                        f"Increase {unprofitable_items[0]['name']} price by ${unprofitable_items[0]['cost'] * 0.15:.2f}",
                        f"Review recipe for {unprofitable_items[1]['name']} to reduce costs",
                        "Consider removing or replacing consistently unprofitable items"
                    ]
                })
            
            # Generate insights for highly profitable items
            if profitable_items:
                # Sort by quantity sold (descending)
                profitable_items.sort(key=lambda x: x['quantity_sold'], reverse=True)
                
                insights.append({
                    'type': 'menu_stars',
                    'priority': 'medium',
                    'title': f"⭐ Menu Stars: High Margin + High Volume",
                    'description': f"Found {len(profitable_items)} menu items with excellent margins above 70%",
                    'recommendation': f"Promote these high-margin items to increase overall profitability",
                    'savings_potential': int(sum(item['margin'] * item['quantity_sold'] * 0.2 for item in profitable_items[:3])),
                    'confidence_score': 0.85,
                    'affected_items': [item['name'] for item in profitable_items[:3]],
                    'action_items': [
                        f"Highlight {profitable_items[0]['name']} on menu for increased visibility",
                        "Train staff to recommend these items",
                        "Create combo deals featuring these high-margin items"
                    ]
                })
        
        except Exception as e:
            print(f"Error connecting recipe and sales data: {str(e)}")
        
        return insights
    
    def to_dict(self) -> Dict:
        """Export entire recipe system to dict for serialization"""
        return {
            'recipes': self.recipes,
            'ingredients': self.ingredients,
            'ingredient_prices': self.ingredient_prices,
            'recipe_metrics': self.recipe_metrics,
            'last_updated': self.last_updated.isoformat()
        }
    
    def from_dict(self, data: Dict) -> None:
        """Load recipe system from dict"""
        self.recipes = data.get('recipes', {})
        self.ingredients = data.get('ingredients', {})
        self.ingredient_prices = data.get('ingredient_prices', {})
        self.recipe_metrics = data.get('recipe_metrics', {})
        self.last_updated = datetime.now()
