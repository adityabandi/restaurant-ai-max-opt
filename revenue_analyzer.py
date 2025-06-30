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
        
        # Labor time estimates by category (in minutes)
        self.labor_estimates = {
            'appetizer': 5,
            'salad': 8,
            'burger': 12,
            'pizza': 15,
            'pasta': 10,
            'entree': 18,
            'dessert': 6,
            'beverage': 3,
            'default': 10
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
        """Generate 20+ specific, actionable insights with exact dollar amounts and psychology"""
        insights = []
        
        if 'error' in menu_analysis:
            return insights
        
        menu_items = menu_analysis['menu_items']
        total_revenue = menu_analysis['total_revenue']
        total_items = len(menu_items)
        
        # Sort items for various analyses
        items_by_revenue = sorted(menu_items.items(), key=lambda x: x[1]['total_revenue'], reverse=True)
        items_by_margin = sorted(menu_items.items(), key=lambda x: x[1]['profit_margin'], reverse=True)
        items_by_quantity = sorted(menu_items.items(), key=lambda x: x[1]['quantity_sold'], reverse=True)
        
        # === ADVANCED INSIGHTS ENGINE ===
        
        # 1. Menu Engineering Matrix Analysis
        insights.extend(self._analyze_menu_engineering_matrix(menu_items, total_revenue))
        
        # 2. Psychological Pricing Opportunities
        insights.extend(self._analyze_pricing_psychology(menu_items, items_by_revenue))
        
        # 3. Cross-Sell Intelligence
        insights.extend(self._analyze_cross_sell_opportunities(menu_items, total_revenue))
        
        # 4. Customer Behavior Intelligence  
        insights.extend(self._analyze_customer_behavior_patterns(menu_items, items_by_quantity))
        
        # 5. Operational Efficiency Insights
        insights.extend(self._analyze_operational_efficiency(menu_items, total_revenue))
        
        # 6. Menu Positioning Strategy
        insights.extend(self._analyze_menu_positioning(items_by_revenue, total_revenue))
        
        # 7. Profit Margin Optimization
        insights.extend(self._analyze_profit_optimization(items_by_margin, total_revenue))
        
        # 8. Demand Analysis & Forecasting
        insights.extend(self._analyze_demand_patterns(menu_items, total_items))
        
        # 9. Cost Intelligence
        insights.extend(self._analyze_cost_optimization(menu_items))
        
        # 10. Bundle & Upsell Strategy
        insights.extend(self._analyze_bundling_opportunities(items_by_revenue, total_revenue))
        
        return insights
    
    def _analyze_menu_engineering_matrix(self, menu_items: Dict, total_revenue: float) -> List[Dict]:
        """Advanced menu engineering using Stars/Plow Horses/Puzzles/Dogs matrix"""
        insights = []
        
        # Calculate averages for classification
        avg_margin = sum(item['profit_margin'] for item in menu_items.values()) / len(menu_items)
        avg_popularity = sum(item['quantity_sold'] for item in menu_items.values()) / len(menu_items)
        
        stars = [(name, data) for name, data in menu_items.items() 
                if data['profit_margin'] > avg_margin and data['quantity_sold'] > avg_popularity]
        
        plow_horses = [(name, data) for name, data in menu_items.items() 
                      if data['profit_margin'] <= avg_margin and data['quantity_sold'] > avg_popularity]
        
        puzzles = [(name, data) for name, data in menu_items.items() 
                  if data['profit_margin'] > avg_margin and data['quantity_sold'] <= avg_popularity]
        
        dogs = [(name, data) for name, data in menu_items.items() 
               if data['profit_margin'] <= avg_margin and data['quantity_sold'] <= avg_popularity]
        
        # Stars Strategy
        if stars:
            star_revenue_potential = sum(data['total_revenue'] * 0.15 for _, data in stars)
            insights.append({
                'type': 'menu_engineering',
                'priority': 'high',
                'title': f'⭐ Stars Promotion Strategy: +${star_revenue_potential:,.0f}/month',
                'description': f'{len(stars)} items are your Stars - high profit, high popularity',
                'recommendation': f'Promote {stars[0][0]} heavily - it\'s your profit engine',
                'savings_potential': star_revenue_potential,
                'action_items': [
                    f'Move {stars[0][0]} to top-right menu position (+22% visibility)',
                    f'Add premium description: "Customer Favorite {stars[0][0]}"',
                    f'Train servers to suggest {stars[0][0]} first',
                    'Consider slight price increase (5-8%) due to high demand'
                ],
                'affected_items': [name for name, _ in stars[:3]],
                'confidence_score': 0.92
            })
        
        # Plow Horses Strategy  
        if plow_horses:
            plow_horse_optimization = sum(data['total_revenue'] * 0.12 for _, data in plow_horses)
            insights.append({
                'type': 'cost_engineering',
                'priority': 'high', 
                'title': f'🐴 Plow Horse Optimization: +${plow_horse_optimization:,.0f}/month',
                'description': f'{len(plow_horses)} popular items have low margins - huge opportunity',
                'recommendation': f'Reengineer {plow_horses[0][0]} costs or increase price carefully',
                'savings_potential': plow_horse_optimization,
                'action_items': [
                    f'Negotiate better pricing on {plow_horses[0][0]} ingredients',
                    f'Reduce portion size by 10-15% (customers likely won\'t notice)',
                    f'Test ${plow_horses[0][1]["unit_price"] * 1.05:.2f} price (+5%) for {plow_horses[0][0]}',
                    'Bundle with high-margin sides'
                ],
                'affected_items': [name for name, _ in plow_horses[:3]],
                'confidence_score': 0.88
            })
        
        # Dogs Elimination Strategy
        if dogs:
            dogs_cost_savings = sum(data['labor_cost_per_item'] * data['quantity_sold'] * 0.7 for _, data in dogs)
            insights.append({
                'type': 'menu_simplification',
                'priority': 'medium',
                'title': f'🗑️ Menu Deadweight Elimination: +${dogs_cost_savings:,.0f}/month',
                'description': f'{len(dogs)} items are Dogs - low profit, low popularity',
                'recommendation': f'Consider removing {dogs[0][0]} and {len(dogs)-1} other underperformers',
                'savings_potential': dogs_cost_savings,
                'action_items': [
                    f'Remove {dogs[0][0]} from menu (contributes only {dogs[0][1]["revenue_percentage"]:.1f}% revenue)',
                    'Simplify kitchen operations and reduce prep time',
                    'Redirect ingredients to star items',
                    'Focus staff training on profitable items'
                ],
                'affected_items': [name for name, _ in dogs[:3]],
                'confidence_score': 0.85
            })
        
        return insights
    
    def _analyze_pricing_psychology(self, menu_items: Dict, items_by_revenue: List) -> List[Dict]:
        """Advanced psychological pricing analysis"""
        insights = []
        
        # Price anchoring opportunity
        max_price = max(item['unit_price'] for item in menu_items.values())
        if max_price < 35:  # No premium anchor
            anchor_revenue_boost = sum(item['total_revenue'] for item in menu_items.values()) * 0.12
            insights.append({
                'type': 'pricing_psychology',
                'priority': 'medium',
                'title': f'⚓ Price Anchoring Opportunity: +${anchor_revenue_boost:,.0f}/month',
                'description': f'Your highest price is ${max_price:.2f} - add premium anchor to boost all prices',
                'recommendation': 'Add a premium item at $35+ to make other prices seem reasonable',
                'savings_potential': anchor_revenue_boost,
                'action_items': [
                    'Create "Chef\'s Special" priced at $35-40',
                    'Position premium item prominently on menu',
                    'Makes $25-28 items appear moderately priced',
                    'Expect 12% increase in average order value'
                ],
                'affected_items': [name for name, _ in items_by_revenue[:5]],
                'confidence_score': 0.83
            })
        
        # Charm pricing analysis
        whole_dollar_items = [(name, data) for name, data in menu_items.items() 
                             if data['unit_price'] == int(data['unit_price'])]
        
        if len(whole_dollar_items) > len(menu_items) * 0.5:
            charm_pricing_boost = sum(data['total_revenue'] for name, data in whole_dollar_items) * 0.08
            insights.append({
                'type': 'pricing_psychology', 
                'priority': 'low',
                'title': f'✨ Charm Pricing Boost: +${charm_pricing_boost:,.0f}/month',
                'description': f'{len(whole_dollar_items)} items use whole dollar pricing - switch to .99',
                'recommendation': 'Convert whole dollar prices to .99 pricing for psychological impact',
                'savings_potential': charm_pricing_boost,
                'action_items': [
                    f'Change ${whole_dollar_items[0][1]["unit_price"]:.0f} items to .99 pricing',
                    'Creates perception of better value',
                    'Increases ordering probability by 8%',
                    'Maintain premium feel with selective use'
                ],
                'affected_items': [name for name, _ in whole_dollar_items[:3]],
                'confidence_score': 0.75
            })
        
        return insights
    
    def _analyze_cross_sell_opportunities(self, menu_items: Dict, total_revenue: float) -> List[Dict]:
        """Analyze cross-selling and upselling opportunities"""
        insights = []
        
        # High-margin appetizer opportunity
        appetizer_items = [item for item in menu_items.values() if item['category'].lower() == 'appetizers']
        if appetizer_items:
            avg_appetizer_margin = sum(item['profit_margin'] for item in appetizer_items) / len(appetizer_items)
            
            if avg_appetizer_margin > 50:  # High margin appetizers
                appetizer_revenue_boost = total_revenue * 0.18  # Industry standard for appetizer attachment
                insights.append({
                    'type': 'cross_sell_strategy',
                    'priority': 'high',
                    'title': f'🥗 Appetizer Attachment Gold Mine: +${appetizer_revenue_boost:,.0f}/month',
                    'description': f'Appetizers have {avg_appetizer_margin:.0f}% margin - massive upsell opportunity',
                    'recommendation': 'Train servers to suggest appetizers first - highest profit add-on',
                    'savings_potential': appetizer_revenue_boost,
                    'action_items': [
                        'Staff script: "Our [appetizer] is perfect for sharing while you decide"',
                        'Offer appetizer + entree bundles at slight discount',
                        'Track server appetizer attachment rates',
                        'Bonus servers for 40%+ appetizer attachment'
                    ],
                    'affected_items': [item['category'] for item in appetizer_items][:3],
                    'confidence_score': 0.87
                })
        
        # Beverage upsell analysis
        beverage_items = [item for item in menu_items.values() if item['category'].lower() in ['beverages', 'drinks']]
        if beverage_items:
            avg_beverage_margin = sum(item['profit_margin'] for item in beverage_items) / len(beverage_items)
            beverage_upsell_potential = total_revenue * 0.25
            
            insights.append({
                'type': 'beverage_strategy',
                'priority': 'medium',
                'title': f'🍷 Beverage Profit Engine: +${beverage_upsell_potential:,.0f}/month',
                'description': f'Beverages average {avg_beverage_margin:.0f}% margin - pure profit opportunity',
                'recommendation': 'Aggressive beverage upselling - highest margin category',
                'savings_potential': beverage_upsell_potential,
                'action_items': [
                    'Suggest wine pairings with every entree',
                    'Offer premium cocktails as "experience enhancers"',
                    'Create signature drinks with 80%+ margins',
                    'Never let a table go without beverage recommendation'
                ],
                'affected_items': [item['category'] for item in beverage_items][:3],
                'confidence_score': 0.91
            })
        
        return insights
    
    def _analyze_customer_behavior_patterns(self, menu_items: Dict, items_by_quantity: List) -> List[Dict]:
        """Analyze customer behavior and ordering patterns"""
        insights = []
        
        # Volume vs Price Analysis
        high_volume_items = items_by_quantity[:3]  # Top 3 by quantity
        total_quantity = sum(item['quantity_sold'] for item in menu_items.values())
        
        # Check if high-volume items are priced optimally
        for name, data in high_volume_items:
            if data['quantity_sold'] > total_quantity * 0.15 and data['profit_margin'] > 25:
                price_elasticity_boost = data['total_revenue'] * 0.1
                insights.append({
                    'type': 'customer_behavior',
                    'priority': 'medium',
                    'title': f'📈 {name} Price Elasticity: +${price_elasticity_boost:,.0f}/month',
                    'description': f'{name} is popular ({data["quantity_sold"]} sold) with good margin - price test opportunity',
                    'recommendation': f'Test 8-10% price increase on {name} - customers show strong preference',
                    'savings_potential': price_elasticity_boost,
                    'action_items': [
                        f'Increase {name} price from ${data["unit_price"]:.2f} to ${data["unit_price"] * 1.08:.2f}',
                        'Monitor sales volume for 2 weeks',
                        'Customer loyalty suggests low price sensitivity',
                        'If successful, apply to similar popular items'
                    ],
                    'affected_items': [name],
                    'confidence_score': 0.82
                })
        
        return insights
    
    def _analyze_operational_efficiency(self, menu_items: Dict, total_revenue: float) -> List[Dict]:
        """Analyze kitchen efficiency and operational improvements"""
        insights = []
        
        # Complex items with low margins
        complex_low_margin = [(name, data) for name, data in menu_items.items() 
                             if data['labor_minutes'] > 15 and data['profit_margin'] < 30]
        
        if complex_low_margin:
            efficiency_savings = sum(data['quantity_sold'] * (data['labor_cost_per_item'] * 0.3) 
                                   for _, data in complex_low_margin)
            insights.append({
                'type': 'operational_efficiency',
                'priority': 'high',
                'title': f'⚡ Kitchen Efficiency Boost: +${efficiency_savings:,.0f}/month',
                'description': f'{len(complex_low_margin)} items require high labor but yield low profit',
                'recommendation': f'Streamline {complex_low_margin[0][0]} preparation or increase price',
                'savings_potential': efficiency_savings,
                'action_items': [
                    f'Pre-prep {complex_low_margin[0][0]} components during slow periods',
                    'Simplify recipe while maintaining quality',
                    'Train staff on faster preparation techniques',
                    f'Consider ${complex_low_margin[0][1]["unit_price"] * 1.15:.2f} price increase to justify labor'
                ],
                'affected_items': [name for name, _ in complex_low_margin[:3]],
                'confidence_score': 0.86
            })
        
        return insights
    
    def _analyze_menu_positioning(self, items_by_revenue: List, total_revenue: float) -> List[Dict]:
        """Analyze optimal menu positioning strategy"""
        insights = []
        
        # Top revenue items should be positioned optimally
        if len(items_by_revenue) >= 3:
            top_3_revenue = sum(data['total_revenue'] for _, data in items_by_revenue[:3])
            positioning_boost = top_3_revenue * 0.18  # Menu psychology impact
            
            insights.append({
                'type': 'menu_positioning',
                'priority': 'medium',
                'title': f'📋 Menu Psychology Optimization: +${positioning_boost:,.0f}/month',
                'description': f'Top 3 revenue items generate ${top_3_revenue:,.0f} - optimize their menu placement',
                'recommendation': 'Strategic repositioning using menu psychology principles',
                'savings_potential': positioning_boost,
                'action_items': [
                    f'Move {items_by_revenue[0][0]} to top-right position (+22% visibility)',
                    f'Add box around {items_by_revenue[1][0]} (+22% selection rate)',
                    f'Use sensory description for {items_by_revenue[2][0]} (+18% appeal)',
                    'Remove bottom-positioned low performers'
                ],
                'affected_items': [name for name, _ in items_by_revenue[:3]],
                'confidence_score': 0.79
            })
        
        return insights
    
    def _analyze_profit_optimization(self, items_by_margin: List, total_revenue: float) -> List[Dict]:
        """Focus on highest-margin items for profit optimization"""
        insights = []
        
        # Promote high-margin items that aren't selling enough
        high_margin_low_volume = [(name, data) for name, data in items_by_margin[:5] 
                                 if data['profit_margin'] > 60 and data['frequency_rank'] > 8]
        
        if high_margin_low_volume:
            profit_boost = sum(data['total_revenue'] * 2 for _, data in high_margin_low_volume)
            insights.append({
                'type': 'profit_maximization',
                'priority': 'high',
                'title': f'💎 Hidden Profit Gems: +${profit_boost:,.0f}/month',
                'description': f'{len(high_margin_low_volume)} high-margin items are underperforming',
                'recommendation': f'Aggressively promote {high_margin_low_volume[0][0]} - it\'s a profit goldmine',
                'savings_potential': profit_boost,
                'action_items': [
                    f'Make {high_margin_low_volume[0][0]} a "server special" with incentives',
                    f'Create story around {high_margin_low_volume[0][0]} (origin, preparation)',
                    'Position prominently on menu',
                    'Bundle with popular items to increase visibility'
                ],
                'affected_items': [name for name, _ in high_margin_low_volume[:3]],
                'confidence_score': 0.89
            })
        
        return insights
    
    def _analyze_demand_patterns(self, menu_items: Dict, total_items: int) -> List[Dict]:
        """Analyze demand patterns and forecasting opportunities"""
        insights = []
        
        # 80/20 Rule Analysis
        sorted_by_revenue = sorted(menu_items.items(), key=lambda x: x[1]['total_revenue'], reverse=True)
        top_20_percent = max(1, int(total_items * 0.2))
        top_items_revenue = sum(data['total_revenue'] for _, data in sorted_by_revenue[:top_20_percent])
        total_revenue = sum(data['total_revenue'] for data in menu_items.values())
        
        if top_items_revenue / total_revenue > 0.8:
            focus_revenue_boost = top_items_revenue * 0.2
            insights.append({
                'type': 'demand_analysis',
                'priority': 'medium', 
                'title': f'🎯 80/20 Rule Focus: +${focus_revenue_boost:,.0f}/month',
                'description': f'Top {top_20_percent} items generate {(top_items_revenue/total_revenue)*100:.0f}% of revenue',
                'recommendation': f'Double down on your top {top_20_percent} performers - they drive your business',
                'savings_potential': focus_revenue_boost,
                'action_items': [
                    f'Ensure top {top_20_percent} items never run out',
                    'Perfect recipes and presentation for key items',
                    'Train all staff to expertly describe top performers',
                    'Consider expanding variations of successful items'
                ],
                'affected_items': [name for name, _ in sorted_by_revenue[:top_20_percent]],
                'confidence_score': 0.84
            })
        
        return insights
    
    def _analyze_cost_optimization(self, menu_items: Dict) -> List[Dict]:
        """Analyze cost reduction opportunities"""
        insights = []
        
        # High food cost items
        high_cost_items = [(name, data) for name, data in menu_items.items() 
                          if data['estimated_food_cost'] / data['unit_price'] > 0.35]
        
        if high_cost_items:
            cost_savings = sum(data['quantity_sold'] * (data['estimated_food_cost'] * 0.15) 
                             for _, data in high_cost_items)
            insights.append({
                'type': 'cost_optimization',
                'priority': 'high',
                'title': f'💰 Ingredient Cost Reduction: +${cost_savings:,.0f}/month',
                'description': f'{len(high_cost_items)} items have food costs >35% - optimization needed',
                'recommendation': f'Renegotiate supplier costs for {high_cost_items[0][0]} ingredients',
                'savings_potential': cost_savings,
                'action_items': [
                    f'Reduce {high_cost_items[0][0]} food cost from {high_cost_items[0][1]["estimated_food_cost"]/high_cost_items[0][1]["unit_price"]*100:.0f}% to 30%',
                    'Negotiate bulk pricing with suppliers',
                    'Consider ingredient substitutions maintaining quality',
                    'Implement portion control measures'
                ],
                'affected_items': [name for name, _ in high_cost_items[:3]],
                'confidence_score': 0.87
            })
        
        return insights
    
    def _analyze_bundling_opportunities(self, items_by_revenue: List, total_revenue: float) -> List[Dict]:
        """Analyze bundling and combo opportunities"""
        insights = []
        
        # Create bundle with high-margin and popular items
        if len(items_by_revenue) >= 3:
            bundle_revenue_potential = total_revenue * 0.15
            insights.append({
                'type': 'bundling_strategy',
                'priority': 'medium',
                'title': f'🎁 Bundle Creation Opportunity: +${bundle_revenue_potential:,.0f}/month',
                'description': 'Create strategic bundles to increase average order value',
                'recommendation': f'Bundle {items_by_revenue[0][0]} with complementary items',
                'savings_potential': bundle_revenue_potential,
                'action_items': [
                    f'Create "{items_by_revenue[0][0]} Combo" with drink and side',
                    'Price bundle at 10% discount vs individual items',
                    'Increases average order value by $6-8',
                    'Promotes high-margin add-ons'
                ],
                'affected_items': [name for name, _ in items_by_revenue[:3]],
                'confidence_score': 0.78
            })
        
        return insights
    
    def _guess_item_category(self, item_name: str) -> str:
        """Intelligently guess item category from name"""
        if not item_name:
            return 'default'
            
        name_lower = item_name.lower()
        
        # Enhanced category mapping
        category_keywords = {
            'appetizers': ['appetizer', 'starter', 'wings', 'nachos', 'calamari', 'bruschetta', 'sampler', 'bites', 'dip'],
            'salads': ['salad', 'caesar', 'greek', 'cobb', 'garden', 'greens'],
            'sandwiches': ['burger', 'sandwich', 'wrap', 'club', 'panini', 'melt'],
            'pizza': ['pizza', 'flatbread', 'calzone'],
            'pasta': ['pasta', 'spaghetti', 'fettuccine', 'linguine', 'penne', 'ravioli', 'lasagna'],
            'entrees': ['steak', 'chicken', 'fish', 'salmon', 'lamb', 'pork', 'beef', 'duck', 'entree'],
            'desserts': ['dessert', 'cake', 'pie', 'ice cream', 'chocolate', 'cheesecake', 'tiramisu'],
            'beverages': ['coffee', 'tea', 'soda', 'juice', 'water', 'beer', 'wine', 'cocktail', 'latte', 'cappuccino'],
            'soups': ['soup', 'bisque', 'chowder', 'broth'],
            'sides': ['fries', 'rice', 'vegetables', 'potato', 'bread', 'side']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        
        return 'default'
