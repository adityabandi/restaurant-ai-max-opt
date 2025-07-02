"""
Hybrid AI System for Restaurant Analytics
Uses Haiku for simple tasks (cheap) and Sonnet for complex insights (powerful)
"""

import anthropic
import os
from typing import Dict, Optional, List, Any
import json
import pandas as pd
try:
    import streamlit as st
except ImportError:
    st = None

class HybridAI:
    """Intelligent AI model selection based on task complexity"""
    
    # Task complexity mapping
    TASK_COMPLEXITY = {
        'file_parsing': 'simple',
        'column_mapping': 'simple',
        'data_validation': 'simple',
        'pattern_detection': 'simple',
        'profit_analysis': 'complex',
        'menu_optimization': 'complex',
        'predictive_insights': 'complex',
        'natural_language_query': 'complex',
        'comprehensive_report': 'complex'
    }
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Anthropic client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key and st and hasattr(st, 'secrets'):
            try:
                api_key = st.secrets.get('ANTHROPIC_API_KEY')
            except:
                pass
        
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
    
    def is_available(self) -> bool:
        """Check if AI is available"""
        return self.client is not None
    
    def analyze(self, task_type: str, data: str, instructions: str, 
               force_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze data with appropriate AI model
        
        Args:
            task_type: Type of task (e.g., 'file_parsing', 'profit_analysis')
            data: Data to analyze
            instructions: Specific instructions for the AI
            force_model: Force a specific model ('haiku' or 'sonnet')
        
        Returns:
            Dict with results and metadata
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'AI not available. Add ANTHROPIC_API_KEY.',
                'fallback_used': True
            }
        
        # Determine model based on task complexity
        if force_model:
            model = self._get_model_name(force_model)
        else:
            complexity = self.TASK_COMPLEXITY.get(task_type, 'complex')
            model = self._get_model_name('haiku' if complexity == 'simple' else 'sonnet')
        
        # Prepare prompt
        prompt = self._prepare_prompt(task_type, data, instructions)
        
        try:
            # Make API call
            message = self.client.messages.create(
                model=model,
                max_tokens=1500 if 'haiku' in model else 2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Try to parse JSON response
            try:
                result = json.loads(response_text)
            except:
                result = {'raw_response': response_text}
            
            return {
                'success': True,
                'result': result,
                'model_used': model,
                'task_type': task_type,
                'cost_estimate': self._estimate_cost(model, len(prompt), len(response_text))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_attempted': model,
                'fallback_available': True
            }
    
    def _get_model_name(self, model_type: str) -> str:
        """Get full model name"""
        models = {
            'haiku': 'claude-3-haiku-20240307',
            'sonnet': 'claude-3-sonnet-20240229',
            'opus': 'claude-3-opus-20240229'  # Only for critical tasks
        }
        return models.get(model_type, models['haiku'])
    
    def _prepare_prompt(self, task_type: str, data: str, instructions: str) -> str:
        """Prepare task-specific prompts"""
        
        base_prompts = {
            'file_parsing': """
                Analyze this file data and identify:
                1. Data type (sales, inventory, etc.)
                2. POS system if detectable
                3. Column mappings
                
                Data: {data}
                
                {instructions}
                
                Respond with JSON: {{"data_type": "", "pos_system": "", "columns": {{}}}}
            """,
            
            'profit_analysis': """
                You are a restaurant profit optimization expert. Analyze this data deeply.
                
                Restaurant Data:
                {data}
                
                {instructions}
                
                Provide comprehensive insights including:
                1. TOP 3 PROFIT LEAKS (with dollar amounts)
                2. IMMEDIATE ACTIONS (what to do TODAY)
                3. REVENUE OPPORTUNITIES (specific tactics)
                4. RISK WARNINGS (what could hurt profits)
                
                Be specific with numbers and actionable recommendations.
            """,
            
            'menu_optimization': """
                You are a menu engineering expert. Analyze this menu data for maximum profitability.
                
                Menu Data:
                {data}
                
                {instructions}
                
                Provide:
                1. PRICING RECOMMENDATIONS (specific items and amounts)
                2. MENU ENGINEERING MATRIX (stars, dogs, etc.)
                3. PSYCHOLOGICAL PRICING TACTICS
                4. EXPECTED PROFIT IMPACT
                
                Use restaurant industry best practices and pricing psychology.
            """,
            
            'predictive_insights': """
                Analyze historical patterns to predict future performance.
                
                Historical Data:
                {data}
                
                {instructions}
                
                Provide:
                1. NEXT 7 DAY FORECAST
                2. SEASONAL PATTERNS
                3. RISK FACTORS
                4. OPTIMIZATION OPPORTUNITIES
                
                Include confidence levels and assumptions.
            """
        }
        
        template = base_prompts.get(task_type, """
            Analyze this data according to the instructions.
            
            Data: {data}
            
            Instructions: {instructions}
            
            Provide clear, actionable insights.
        """)
        
        return template.format(data=data, instructions=instructions)
    
    def _estimate_cost(self, model: str, input_chars: int, output_chars: int) -> Dict[str, float]:
        """Estimate API cost"""
        # Rough token estimation (1 token ≈ 4 characters)
        input_tokens = input_chars / 4
        output_tokens = output_chars / 4
        
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25},
            'claude-3-sonnet-20240229': {'input': 3.00, 'output': 15.00},
            'claude-3-opus-20240229': {'input': 15.00, 'output': 75.00}
        }
        
        model_pricing = pricing.get(model, pricing['claude-3-haiku-20240307'])
        
        input_cost = (input_tokens / 1_000_000) * model_pricing['input']
        output_cost = (output_tokens / 1_000_000) * model_pricing['output']
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost,
            'model': model.split('-')[2]  # haiku, sonnet, or opus
        }
    
    def batch_analyze(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple tasks efficiently
        
        Args:
            tasks: List of task dictionaries with keys: task_type, data, instructions
        
        Returns:
            List of results
        """
        results = []
        total_cost = 0
        
        for task in tasks:
            result = self.analyze(
                task_type=task['task_type'],
                data=task['data'],
                instructions=task.get('instructions', ''),
                force_model=task.get('force_model')
            )
            
            results.append(result)
            
            if result.get('success') and 'cost_estimate' in result:
                total_cost += result['cost_estimate']['total_cost']
        
        return {
            'results': results,
            'total_cost_estimate': total_cost,
            'tasks_completed': len([r for r in results if r.get('success')]),
            'tasks_failed': len([r for r in results if not r.get('success')])
        }


class SmartAnalytics:
    """High-level analytics using hybrid AI"""
    
    def __init__(self):
        self.ai = HybridAI()
    
    def analyze_profit_opportunities(self, sales_data: pd.DataFrame, 
                                   inventory_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        Comprehensive profit analysis using Sonnet
        """
        # Prepare data summary
        data_summary = self._prepare_data_summary(sales_data, inventory_data)
        
        # Use Sonnet for complex analysis
        result = self.ai.analyze(
            task_type='profit_analysis',
            data=data_summary,
            instructions="""
                Find specific profit leaks and opportunities.
                Include:
                - Food cost optimization
                - Menu pricing issues  
                - Waste reduction opportunities
                - Labor efficiency insights
                - Seasonal patterns
                
                Provide dollar amounts and percentages where possible.
            """
        )
        
        return result
    
    def optimize_menu(self, menu_data: pd.DataFrame) -> Dict:
        """
        Menu optimization using Sonnet
        """
        # Prepare menu summary
        menu_summary = self._prepare_menu_summary(menu_data)
        
        result = self.ai.analyze(
            task_type='menu_optimization',
            data=menu_summary,
            instructions="""
                Optimize this menu for maximum profitability.
                Consider:
                - Price elasticity
                - Item popularity vs profitability
                - Psychological pricing principles
                - Competitive positioning
                - Bundle opportunities
                
                Rank items by profit potential.
            """
        )
        
        return result
    
    def quick_file_analysis(self, file_sample: str, filename: str) -> Dict:
        """
        Quick file analysis using Haiku (cheap)
        """
        result = self.ai.analyze(
            task_type='file_parsing',
            data=file_sample,
            instructions=f"Filename: {filename}. Detect POS system and map columns.",
            force_model='haiku'
        )
        
        return result
    
    def _prepare_data_summary(self, sales_data: pd.DataFrame, 
                            inventory_data: Optional[pd.DataFrame]) -> str:
        """Prepare data summary for AI analysis"""
        summary = []
        
        # Sales summary
        if not sales_data.empty:
            summary.append("SALES DATA:")
            summary.append(f"- Total records: {len(sales_data)}")
            summary.append(f"- Date range: {sales_data.get('date', pd.Series()).min()} to {sales_data.get('date', pd.Series()).max()}")
            
            if 'total_amount' in sales_data.columns:
                summary.append(f"- Total revenue: ${sales_data['total_amount'].sum():,.2f}")
                summary.append(f"- Average transaction: ${sales_data['total_amount'].mean():.2f}")
            
            if 'item_name' in sales_data.columns:
                top_items = sales_data.groupby('item_name')['quantity'].sum().nlargest(10)
                summary.append("\nTOP 10 ITEMS BY QUANTITY:")
                for item, qty in top_items.items():
                    summary.append(f"- {item}: {qty}")
            
            if 'category' in sales_data.columns:
                category_sales = sales_data.groupby('category')['total_amount'].sum()
                summary.append("\nSALES BY CATEGORY:")
                for cat, amount in category_sales.items():
                    summary.append(f"- {cat}: ${amount:,.2f}")
        
        # Inventory summary
        if inventory_data is not None and not inventory_data.empty:
            summary.append("\n\nINVENTORY DATA:")
            summary.append(f"- Total items: {len(inventory_data)}")
            
            if 'quantity_on_hand' in inventory_data.columns:
                low_stock = inventory_data[inventory_data['quantity_on_hand'] < 10]
                if not low_stock.empty:
                    summary.append(f"\nLOW STOCK ITEMS ({len(low_stock)}):")
                    for _, item in low_stock.head(5).iterrows():
                        summary.append(f"- {item.get('item_name', 'Unknown')}: {item['quantity_on_hand']} units")
        
        return '\n'.join(summary)
    
    def _prepare_menu_summary(self, menu_data: pd.DataFrame) -> str:
        """Prepare menu summary for AI analysis"""
        summary = []
        
        summary.append("MENU ANALYSIS:")
        summary.append(f"Total items: {len(menu_data)}")
        
        if 'price' in menu_data.columns and 'cost' in menu_data.columns:
            menu_data['profit'] = menu_data['price'] - menu_data['cost']
            menu_data['margin'] = (menu_data['profit'] / menu_data['price'] * 100).round(1)
            
            summary.append(f"\nPROFIT MARGINS:")
            summary.append(f"- Average margin: {menu_data['margin'].mean():.1f}%")
            summary.append(f"- Items below 60% margin: {len(menu_data[menu_data['margin'] < 60])}")
            
            summary.append(f"\nPRICE RANGES:")
            summary.append(f"- Lowest: ${menu_data['price'].min():.2f}")
            summary.append(f"- Highest: ${menu_data['price'].max():.2f}")
            summary.append(f"- Average: ${menu_data['price'].mean():.2f}")
        
        if 'quantity_sold' in menu_data.columns:
            menu_data['revenue'] = menu_data['price'] * menu_data['quantity_sold']
            
            top_revenue = menu_data.nlargest(10, 'revenue')[['item_name', 'price', 'margin', 'revenue']]
            summary.append(f"\nTOP REVENUE ITEMS:")
            for _, item in top_revenue.iterrows():
                summary.append(f"- {item['item_name']}: ${item['price']:.2f} | {item['margin']:.1f}% margin | ${item['revenue']:,.0f} revenue")
        
        return '\n'.join(summary)