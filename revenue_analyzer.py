import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import statistics

class RevenueAnalyzer:
    def __init__(self):
        # Comprehensive industry intelligence based on restaurant research
        self.industry_benchmarks = {
            'food_cost_percentage': 0.28,  # 28% industry average
            'labor_cost_percentage': 0.30,  # 30% industry average
            'profit_margin_target': 0.15,   # 15% target profit margin
            'inventory_turnover_target': 12,  # 12 times per year
            'prime_cost_target': 0.58,      # Food + Labor should be <58%
            'beverage_markup': 4.0,         # 4x cost for beverages
            'wine_markup': 3.5,             # 3.5x cost for wine
            'liquor_markup': 5.0,           # 5x cost for liquor
        }
        
        # Sophisticated menu engineering matrix
        self.menu_engineering = {
            'stars': {           # High profit, high popularity
                'profit_margin': 0.70,
                'popularity_threshold': 0.70,
                'strategy': 'promote_heavily',
                'price_elasticity': 'low',    # Can increase prices
                'staff_training_priority': 'high'
            },
            'plow_horses': {     # Low profit, high popularity
                'profit_margin': 0.30,
                'popularity_threshold': 0.70,
                'strategy': 'reengineer_costs',
                'price_elasticity': 'medium',
                'action': 'reduce_costs_or_increase_price'
            },
            'puzzles': {         # High profit, low popularity
                'profit_margin': 0.70,
                'popularity_threshold': 0.30,
                'strategy': 'promote_or_eliminate',
                'marketing_potential': 'high'
            },
            'dogs': {            # Low profit, low popularity
                'profit_margin': 0.30,
                'popularity_threshold': 0.30,
                'strategy': 'eliminate_immediately',
                'opportunity_cost': 'high'
            }
        }
        
        # Advanced labor modeling by complexity and kitchen station
        self.labor_intelligence = {
            'prep_complexity': {
                'simple': {'time_minutes': 3, 'skill_level': 1, 'wage_multiplier': 1.0},
                'moderate': {'time_minutes': 8, 'skill_level': 2, 'wage_multiplier': 1.2},
                'complex': {'time_minutes': 15, 'skill_level': 3, 'wage_multiplier': 1.5},
                'chef_level': {'time_minutes': 25, 'skill_level': 4, 'wage_multiplier': 2.0}
            },
            'kitchen_stations': {
                'cold_station': {'efficiency': 1.2, 'avg_wage': 16},
                'saute_station': {'efficiency': 0.9, 'avg_wage': 22},
                'grill_station': {'efficiency': 1.0, 'avg_wage': 20},
                'fryer_station': {'efficiency': 1.3, 'avg_wage': 18},
                'pastry_station': {'efficiency': 0.7, 'avg_wage': 24}
            },
            'service_factors': {
                'rush_hour_multiplier': 1.4,      # Takes 40% longer during rush
                'weekend_multiplier': 1.2,        # Slightly slower on weekends
                'new_staff_multiplier': 1.8,      # New staff takes 80% longer
                'experienced_staff_multiplier': 0.8  # Experienced staff 20% faster
            }
        }
        
        # Psychology-based pricing intelligence
        self.pricing_psychology = {
            'price_anchoring': {
                'expensive_anchor_boost': 1.15,   # Having expensive items boosts others
                'decoy_effect_power': 1.25,       # Strategic decoy pricing
                'charm_pricing_impact': 1.08      # .99 vs .00 pricing
            },
            'menu_placement': {
                'top_right_premium': 1.12,        # Items here sell 12% more
                'eye_level_boost': 1.08,          # Eye-level items get attention
                'bottom_penalty': 0.85,           # Bottom items sell less
                'box_highlight_boost': 1.22       # Boxed items get 22% more orders
            },
            'description_power': {
                'sensory_words_boost': 1.18,      # "Crispy", "tender", "rich"
                'origin_story_boost': 1.12,       # "Grandma's recipe", "farm-fresh"
                'health_halo_boost': 1.09,        # "Organic", "local", "sustainable"
                'social_proof_boost': 1.15        # "Customer favorite", "most popular"
            }
        }
        
        # Advanced cost modeling
        self.cost_intelligence = {
            'hidden_costs': {
                'plate_cost': 0.75,               # Average plate/serving cost
                'utility_per_item': 0.45,         # Gas/electric per item
                'waste_factor': 1.08,             # 8% waste on average
                'comp_factor': 1.02,              # 2% comps/mistakes
                'credit_card_fees': 0.035,        # 3.5% payment processing
                'delivery_platform_fee': 0.25     # Platform commission
            },
            'seasonal_cost_variance': {
                'summer_produce_discount': 0.85,   # 15% cheaper in season
                'winter_produce_premium': 1.25,    # 25% more expensive
                'holiday_protein_premium': 1.35,   # 35% more during holidays
                'supply_chain_disruption': 1.45    # 45% increase during shortages
            },
            'volume_discount_opportunities': {
                'bulk_purchasing_savings': 0.12,   # 12% savings on bulk orders
                'supplier_consolidation_savings': 0.08,  # 8% from fewer vendors
                'seasonal_buying_savings': 0.15    # 15% from seasonal purchasing
            }
        }
        
        # Customer behavior intelligence
        self.customer_intelligence = {
            'ordering_patterns': {
                'appetizer_attachment_rate': 0.35,     # 35% order appetizers
                'dessert_attachment_rate': 0.22,       # 22% order desserts
                'alcohol_attachment_rate': 0.45,       # 45% order alcohol
                'upsell_success_rate': 0.28,           # 28% accept upsells
                'side_dish_penetration': 0.60          # 60% add sides
            },
            'psychological_triggers': {
                'scarcity_urgency_boost': 1.18,        # "Limited time" items
                'social_validation_boost': 1.12,       # "Others also ordered"
                'bundle_perception_value': 1.15,       # Bundles feel like deals
                'premium_positioning_tolerance': 1.08   # Premium prices accepted
            },
            'seasonal_behavior': {
                'january_health_conscious': 1.25,      # Health items sell 25% more
                'february_comfort_craving': 1.18,      # Comfort food boost
                'summer_lighter_fare': 1.20,           # Salads, cold items
                'fall_harvest_appeal': 1.15,           # Seasonal ingredients
                'holiday_indulgence': 1.30             # Premium/indulgent items
            }
        }
    
    def analyze_menu_performance(self, sales_data: List[Dict]) -> Dict:
        """Comprehensive menu performance analysis"""
        if not sales_data:
            return {'error': 'No sales data provided'}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(sales_data)
        
        # Ensure required columns exist
        required_cols = ['item_name']
        if not all(col in df.columns for col in required_cols):
            return {'error': 'Missing required columns: item_name'}
        
        # Calculate key metrics for each item
        menu_analysis = {}
        total_revenue = 0
        total_quantity = 0
        
        for item_name in df['item_name'].unique():
            if pd.isna(item_name) or item_name == '':
                continue
                
            item_data = df[df['item_name'] == item_name]
            
            # Basic metrics
            quantity_sold = item_data.get('quantity', 1).sum()
            unit_price = item_data.get('price', item_data.get('total_amount', 0)).mean()
            total_item_revenue = quantity_sold * unit_price
            
            # Labor cost estimation
            category = self._guess_item_category(item_name)
            labor_minutes = self.labor_estimates.get(category, self.labor_estimates['default'])
            labor_cost_per_item = (labor_minutes / 60) * 15  # $15/hour average
            
            # Food cost estimation (industry average 28% of selling price)
            estimated_food_cost = unit_price * 0.28
            
            # Calculate margins
            total_cost_per_item = estimated_food_cost + labor_cost_per_item
            profit_per_item = unit_price - total_cost_per_item
            profit_margin = (profit_per_item / unit_price) * 100 if unit_price > 0 else 0
            
            menu_analysis[item_name] = {
                'quantity_sold': quantity_sold,
                'unit_price': unit_price,
                'total_revenue': total_item_revenue,
                'estimated_food_cost': estimated_food_cost,
                'labor_cost_per_item': labor_cost_per_item,
                'total_cost_per_item': total_cost_per_item,
                'profit_per_item': profit_per_item,
                'profit_margin': profit_margin,
                'category': category,
                'labor_minutes': labor_minutes,
                'revenue_percentage': 0,  # Will calculate after totals
                'frequency_rank': 0
            }
            
            total_revenue += total_item_revenue
            total_quantity += quantity_sold
        
        # Calculate revenue percentages and rankings
        sorted_by_revenue = sorted(menu_analysis.items(), key=lambda x: x[1]['total_revenue'], reverse=True)
        sorted_by_quantity = sorted(menu_analysis.items(), key=lambda x: x[1]['quantity_sold'], reverse=True)
        
        for i, (item_name, data) in enumerate(sorted_by_revenue):
            menu_analysis[item_name]['revenue_percentage'] = (data['total_revenue'] / total_revenue) * 100
            menu_analysis[item_name]['revenue_rank'] = i + 1
        
        for i, (item_name, data) in enumerate(sorted_by_quantity):
            menu_analysis[item_name]['frequency_rank'] = i + 1
        
        return {
            'menu_items': menu_analysis,
            'total_revenue': total_revenue,
            'total_quantity': total_quantity,
            'total_items': len(menu_analysis),
            'analysis_date': datetime.now().isoformat()
        }
    
    def generate_actionable_insights(self, menu_analysis: Dict, user_context: Dict = None) -> List[Dict]:
        """Generate specific, actionable insights with dollar amounts"""
        insights = []
        
        if 'error' in menu_analysis:
            return insights
        
        menu_items = menu_analysis['menu_items']
        total_revenue = menu_analysis['total_revenue']
        
        # 1. Identify profit killers
        low_margin_items = [
            (name, data) for name, data in menu_items.items() 
            if data['profit_margin'] < 10  # Less than 10% margin
        ]
        
        if low_margin_items:
            # Calculate potential savings
            total_low_margin_revenue = sum(data['total_revenue'] for _, data in low_margin_items)
            potential_monthly_savings = sum(
                data['quantity_sold'] * (data['unit_price'] * 0.15 - data['profit_per_item'])
                for _, data in low_margin_items
            )
            
            insight = {
                'type': 'profit_optimization',
                'priority': 'high',
                'title': f'💰 Profit Killers Detected: {len(low_margin_items)} Items',
                'description': f'{len(low_margin_items)} menu items have margins below 10%',
                'recommendation': f'Fix pricing on {low_margin_items[0][0]} and {len(low_margin_items)-1} other items',
                'savings_potential': potential_monthly_savings,
                'action_items': [
                    f'Increase price of {low_margin_items[0][0]} by ${(low_margin_items[0][1]["unit_price"] * 0.15):.2f}',
                    'Review ingredient costs with suppliers',
                    'Consider portion size adjustments'
                ],
                'affected_items': [name for name, _ in low_margin_items[:3]]
            }
            insights.append(insight)
        
        # 2. Identify revenue opportunities (high demand, low price)
        high_demand_items = [
            (name, data) for name, data in menu_items.items()
            if data['frequency_rank'] <= 5 and data['profit_margin'] > 20
        ]
        
        if high_demand_items:
            price_increase_opportunity = sum(
                data['quantity_sold'] * data['unit_price'] * 0.08  # 8% price increase
                for _, data in high_demand_items
            )
            
            insight = {
                'type': 'revenue_optimization',
                'priority': 'medium',
                'title': f'🚀 Price Increase Opportunity: ${price_increase_opportunity:,.0f}/month',
                'description': f'Top {len(high_demand_items)} items can support 8-12% price increases',
                'recommendation': f'Test 8% price increase on {high_demand_items[0][0]}',
                'savings_potential': price_increase_opportunity,
                'action_items': [
                    f'Increase {high_demand_items[0][0]} price from ${high_demand_items[0][1]["unit_price"]:.2f} to ${high_demand_items[0][1]["unit_price"] * 1.08:.2f}',
                    'Monitor customer response for 2 weeks',
                    'Apply to other high-demand items if successful'
                ],
                'affected_items': [name for name, _ in high_demand_items[:3]]
            }
            insights.append(insight)
        
        # 3. Identify menu deadweight (low sales, taking up space)
        total_items = len(menu_items)
        deadweight_items = [
            (name, data) for name, data in menu_items.items()
            if data['revenue_percentage'] < 2 and data['frequency_rank'] > total_items * 0.7
        ]
        
        if deadweight_items:
            menu_simplification_savings = sum(
                data['quantity_sold'] * data['labor_cost_per_item'] * 0.5  # 50% labor savings
                for _, data in deadweight_items
            )
            
            insight = {
                'type': 'menu_optimization',
                'priority': 'high',
                'title': f'📋 Menu Deadweight: Remove {len(deadweight_items)} Items',
                'description': f'{len(deadweight_items)} items contribute <2% of revenue each',
                'recommendation': f'Remove {deadweight_items[0][0]} and {len(deadweight_items)-1} other low performers',
                'savings_potential': menu_simplification_savings + 50,  # + kitchen efficiency
                'action_items': [
                    f'Remove {deadweight_items[0][0]} from menu',
                    'Redirect ingredients to popular items',
                    'Simplify kitchen operations'
                ],
                'affected_items': [name for name, _ in deadweight_items[:3]]
            }
            insights.append(insight)
        
        # 4. Labor efficiency opportunities
        high_labor_items = [
            (name, data) for name, data in menu_items.items()
            if data['labor_minutes'] > 15 and data['profit_margin'] < 25
        ]
        
        if high_labor_items:
            labor_optimization_savings = sum(
                data['quantity_sold'] * (data['labor_cost_per_item'] * 0.3)  # 30% labor reduction
                for _, data in high_labor_items
            )
            
            insight = {
                'type': 'labor_optimization',
                'priority': 'medium',
                'title': f'⚡ Labor Efficiency: Save ${labor_optimization_savings:,.0f}/month',
                'description': f'{len(high_labor_items)} items require excessive prep time',
                'recommendation': f'Streamline preparation for {high_labor_items[0][0]}',
                'savings_potential': labor_optimization_savings,
                'action_items': [
                    f'Pre-prep components for {high_labor_items[0][0]}',
                    'Simplify recipe complexity',
                    'Train staff on faster techniques'
                ],
                'affected_items': [name for name, _ in high_labor_items[:3]]
            }
            insights.append(insight)
        
        # 5. Cross-selling opportunities
        high_margin_items = [
            (name, data) for name, data in menu_items.items()
            if data['profit_margin'] > 30 and data['frequency_rank'] > 10
        ]
        
        if high_margin_items:
            cross_sell_opportunity = sum(
                data['quantity_sold'] * data['profit_per_item'] * 2  # Double sales through upselling
                for _, data in high_margin_items[:3]
            )
            
            insight = {
                'type': 'upselling_strategy',
                'priority': 'medium',
                'title': f'🎯 Upselling Gold Mine: ${cross_sell_opportunity:,.0f}/month',
                'description': f'High-margin items with low visibility',
                'recommendation': f'Train staff to upsell {high_margin_items[0][0]}',
                'savings_potential': cross_sell_opportunity,
                'action_items': [
                    f'Add {high_margin_items[0][0]} to server talking points',
                    'Create combo deals featuring high-margin items',
                    'Improve menu placement and descriptions'
                ],
                'affected_items': [name for name, _ in high_margin_items[:3]]
            }
            insights.append(insight)
        
        return insights
    
    def _guess_item_category(self, item_name: str) -> str:
        """Guess item category based on name for labor estimation"""
        item_lower = item_name.lower()
        
        category_keywords = {
            'appetizer': ['appetizer', 'starter', 'wings', 'nachos', 'calamari', 'bruschetta'],
            'salad': ['salad', 'caesar', 'greek', 'cobb'],
            'burger': ['burger', 'sandwich', 'wrap', 'club'],
            'pizza': ['pizza', 'flatbread'],
            'pasta': ['pasta', 'spaghetti', 'fettuccine', 'linguine', 'penne'],
            'entree': ['steak', 'chicken', 'fish', 'salmon', 'lamb', 'pork', 'beef'],
            'dessert': ['dessert', 'cake', 'pie', 'ice cream', 'chocolate', 'cheesecake'],
            'beverage': ['coffee', 'tea', 'soda', 'juice', 'water', 'beer', 'wine', 'cocktail']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in item_lower for keyword in keywords):
                return category
        
        return 'default'
    
    def calculate_inventory_insights(self, inventory_data: List[Dict]) -> List[Dict]:
        """Analyze inventory for cost optimization opportunities"""
        insights = []
        
        if not inventory_data:
            return insights
        
        df = pd.DataFrame(inventory_data)
        
        # High-value inventory analysis
        if 'quantity' in df.columns and 'cost_per_unit' in df.columns:
            df['total_value'] = df['quantity'] * df['cost_per_unit']
            high_value_items = df[df['total_value'] > 500]
            
            if not high_value_items.empty:
                total_tied_up = high_value_items['total_value'].sum()
                potential_savings = total_tied_up * 0.20  # 20% reduction
                
                insight = {
                    'type': 'inventory_optimization',
                    'priority': 'high',
                    'title': f'📦 Inventory Capital Tied Up: ${total_tied_up:,.0f}',
                    'description': f'{len(high_value_items)} items represent ${total_tied_up:,.0f} in inventory',
                    'recommendation': 'Implement just-in-time ordering for high-value items',
                    'savings_potential': potential_savings,
                    'action_items': [
                        'Reduce high-value inventory by 20-30%',
                        'Negotiate shorter delivery cycles',
                        'Track usage patterns weekly'
                    ]
                }
                insights.append(insight)
        
        # Low stock alerts
        if 'quantity' in df.columns:
            low_stock = df[df['quantity'] < 10]
            
            if not low_stock.empty:
                insight = {
                    'type': 'supply_chain_alert',
                    'priority': 'high',
                    'title': f'⚠️ Low Stock Alert: {len(low_stock)} Items',
                    'description': f'{len(low_stock)} items below reorder threshold',
                    'recommendation': 'Immediate reorder needed to prevent stockouts',
                    'savings_potential': 0,
                    'action_items': [
                        'Place orders within 24 hours',
                        'Set up automated reorder alerts',
                        'Review par levels'
                    ]
                }
                insights.append(insight)
        
        return insights
    
    def analyze_supplier_opportunities(self, supplier_data: List[Dict]) -> List[Dict]:
        """Find supplier cost optimization opportunities"""
        insights = []
        
        if not supplier_data:
            return insights
        
        df = pd.DataFrame(supplier_data)
        
        # Group by item to find price differences
        if 'item_name' in df.columns and 'unit_cost' in df.columns:
            item_costs = df.groupby('item_name')['unit_cost'].agg(['count', 'min', 'max', 'mean']).reset_index()
            
            # Find items with multiple suppliers and price differences
            multi_supplier_items = item_costs[item_costs['count'] > 1]
            price_opportunities = multi_supplier_items[multi_supplier_items['max'] > multi_supplier_items['min'] * 1.15]
            
            if not price_opportunities.empty:
                total_savings = 0
                for _, row in price_opportunities.iterrows():
                    monthly_usage = 100  # Estimate
                    savings_per_unit = row['max'] - row['min']
                    total_savings += monthly_usage * savings_per_unit
                
                insight = {
                    'type': 'supplier_optimization',
                    'priority': 'high',
                    'title': f'🏪 Supplier Arbitrage: ${total_savings:,.0f}/month',
                    'description': f'Price differences found across {len(price_opportunities)} items',
                    'recommendation': f'Switch to lower-cost suppliers for key items',
                    'savings_potential': total_savings,
                    'action_items': [
                        'Negotiate price matching with current suppliers',
                        'Test quality with lower-cost alternatives',
                        'Implement dual sourcing strategy'
                    ]
                }
                insights.append(insight)
        
        return insights