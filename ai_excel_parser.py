import pandas as pd
import io
import json
import re
from typing import Dict, List, Tuple, Optional
import anthropic
import os
from datetime import datetime

class AIExcelParser:
    def __init__(self):
        self.anthropic_client = None
        try:
            # 🔑 CLAUDE API INTEGRATION - Ready for future activation
            # To enable AI mode: Add ANTHROPIC_API_KEY to Streamlit Cloud secrets
            # The app automatically switches between AI Enhanced and Smart Analytics modes
            
            api_key = None
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
                    api_key = st.secrets["ANTHROPIC_API_KEY"]
            except:
                pass
            
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY")
            
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            print(f"Note: Running in Smart Analytics mode (no AI key): {e}")
            self.anthropic_client = None
    
    def parse_file(self, file_contents: bytes, filename: str) -> Dict:
        """Main parsing method that uses AI to understand any Excel/CSV format"""
        try:
            # Step 1: Load the file
            df = self._load_file(file_contents, filename)
            
            if df.empty:
                raise Exception("File appears to be empty")
            
            # Step 2: Use AI to understand the structure
            file_analysis = self._analyze_with_ai(df, filename)
            
            # Step 3: Process based on AI understanding
            processed_data = self._process_based_on_analysis(df, file_analysis)
            
            return {
                'success': True,
                'data_type': file_analysis['data_type'],
                'columns_mapped': file_analysis['column_mapping'],
                'rows_processed': len(processed_data),
                'processed_data': processed_data,
                'ai_confidence': file_analysis.get('confidence', 0.85),
                'suggestions': file_analysis.get('suggestions', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'suggestions': self._get_error_suggestions(str(e))
            }
    
    def _load_file(self, file_contents: bytes, filename: str) -> pd.DataFrame:
        """Enhanced file loading with comprehensive fallback strategies"""
        file_extension = filename.lower().split('.')[-1]
        
        # Record errors for better feedback
        error_log = []
        
        try:
            if file_extension == 'csv':
                # Try different encodings and separators with detailed error tracking
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']:
                    for sep in [',', ';', '\t', '|']:
                        try:
                            df = pd.read_csv(io.BytesIO(file_contents), encoding=encoding, sep=sep)
                            if len(df.columns) > 1 and len(df) > 0:
                                print(f"Successfully loaded CSV with encoding {encoding} and separator '{sep}'")
                                return self._clean_dataframe(df)
                        except Exception as e:
                            error_msg = f"Failed with encoding {encoding}, separator '{sep}': {str(e)}"
                            error_log.append(error_msg)
                            continue
                
                # If all standard approaches fail, try to fix corrupted CSV
                try:
                    # Try to decode with replacement of bad characters
                    text_content = file_contents.decode('utf-8', errors='replace')
                    lines = text_content.split('\n')
                    
                    # Filter out problematic lines
                    valid_lines = []
                    for i, line in enumerate(lines):
                        try:
                            if i == 0 or len(line.strip()) > 0:  # Keep header and non-empty lines
                                valid_lines.append(line)
                        except:
                            error_log.append(f"Skipped corrupted line {i}")
                    
                    # Try to parse the cleaned content
                    if valid_lines:
                        cleaned_content = '\n'.join(valid_lines)
                        df = pd.read_csv(io.StringIO(cleaned_content))
                        if len(df.columns) > 1 and len(df) > 0:
                            print("Loaded CSV after repairing corrupted content")
                            return self._clean_dataframe(df)
                except Exception as e:
                    error_log.append(f"Failed to repair CSV: {str(e)}")
            
            elif file_extension in ['xlsx', 'xls']:
                # Try multiple Excel reading approaches
                excel_errors = []
                
                # First try with openpyxl (modern Excel files)
                try:
                    df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
                    if len(df.columns) > 0 and len(df) > 0:
                        print("Successfully loaded Excel with openpyxl engine")
                        return self._clean_dataframe(df)
                except Exception as e:
                    excel_errors.append(f"openpyxl failed: {str(e)}")
                
                # Then try with xlrd (older Excel files)
                try:
                    df = pd.read_excel(io.BytesIO(file_contents), engine='xlrd')
                    if len(df.columns) > 0 and len(df) > 0:
                        print("Successfully loaded Excel with xlrd engine")
                        return self._clean_dataframe(df)
                except Exception as e:
                    excel_errors.append(f"xlrd failed: {str(e)}")
                
                # Try all sheets if first sheet fails
                try:
                    xls = pd.ExcelFile(io.BytesIO(file_contents))
                    for sheet_name in xls.sheet_names:
                        try:
                            df = pd.read_excel(io.BytesIO(file_contents), sheet_name=sheet_name)
                            if len(df.columns) > 0 and len(df) > 0:
                                print(f"Successfully loaded Excel sheet: {sheet_name}")
                                return self._clean_dataframe(df)
                        except:
                            continue
                except Exception as e:
                    excel_errors.append(f"Multi-sheet attempt failed: {str(e)}")
                
                error_log.extend(excel_errors)
            
            # Last resort - try as CSV regardless of extension
            try:
                df = pd.read_csv(io.BytesIO(file_contents))
                if len(df.columns) > 0 and len(df) > 0:
                    print(f"Successfully loaded {file_extension} file as CSV")
                    return self._clean_dataframe(df)
            except Exception as e:
                error_log.append(f"Last resort CSV attempt failed: {str(e)}")
            
            # If we got here, all attempts failed
            error_details = "\n".join(error_log[-5:])  # Last 5 errors
            raise Exception(f"Could not read file after multiple attempts. Last errors:\n{error_details}")
        
        except Exception as e:
            raise Exception(f"File processing error: {str(e)}")
        
        raise Exception("Unable to parse file format. Supported formats: CSV, Excel (.xlsx, .xls)")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize dataframe"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _analyze_with_ai(self, df: pd.DataFrame, filename: str) -> Dict:
        """Smart analysis - try patterns first, AI fallback only when needed"""
        # Step 1: Try smart pattern detection first (fast & free)
        pattern_analysis = self._smart_pattern_detection(df, filename)
        
        # Step 2: Only use AI if pattern detection has low confidence
        if pattern_analysis['confidence'] >= 0.85:
            return pattern_analysis
        
        # Step 3: Use AI for complex cases (only when needed)
        if self.anthropic_client:
            # Prepare sample data for AI analysis
            sample_data = self._prepare_sample_for_ai(df)
            ai_analysis = self._claude_analysis(sample_data, filename)
            
            # Combine AI insights with pattern detection
            return self._merge_analysis(pattern_analysis, ai_analysis)
        else:
            return pattern_analysis
    
    def _prepare_sample_for_ai(self, df: pd.DataFrame) -> str:
        """Prepare sample data for AI analysis"""
        # Get first 5 rows and column info
        sample_rows = min(5, len(df))
        sample_df = df.head(sample_rows)
        
        # Create a structured sample
        sample_info = {
            'columns': list(df.columns),
            'total_rows': len(df),
            'sample_data': []
        }
        
        for _, row in sample_df.iterrows():
            row_data = {}
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    row_data[col] = None
                else:
                    row_data[col] = str(value)[:50]  # Limit length for AI processing
            sample_info['sample_data'].append(row_data)
        
        return json.dumps(sample_info, indent=2)
    
    def _smart_pattern_detection(self, df: pd.DataFrame, filename: str) -> Dict:
        """Advanced pattern detection for common restaurant POS systems"""
        columns = [col.lower() for col in df.columns]
        filename_lower = filename.lower()
        
        # POS System Detection Patterns
        pos_patterns = {
            'square': ['gross sales', 'net sales', 'tax', 'tip', 'fees', 'item name'],
            'toast': ['item name', 'quantity', 'gross', 'discount', 'net'],
            'clover': ['name', 'price', 'quantity', 'amount', 'tax'],
            'resy': ['party size', 'date', 'time', 'covers', 'guest'],
            'opentable': ['reservation', 'covers', 'date', 'time', 'party'],
            'doordash': ['delivery', 'order', 'subtotal', 'delivery fee'],
            'ubereats': ['order', 'delivery', 'pickup', 'subtotal', 'fees']
        }
        
        # Detect POS system
        pos_system = 'unknown'
        pos_confidence = 0.0
        
        for system, patterns in pos_patterns.items():
            matches = sum(1 for pattern in patterns if any(pattern in col for col in columns))
            confidence = matches / len(patterns)
            if confidence > pos_confidence:
                pos_confidence = confidence
                pos_system = system
        
        # Data Type Detection with enhanced patterns
        data_type_patterns = {
            'sales': {
                'required': ['item', 'quantity', 'price'],
                'optional': ['total', 'amount', 'revenue', 'date', 'time'],
                'filename_keywords': ['sales', 'pos', 'transaction', 'revenue']
            },
            'inventory': {
                'required': ['item', 'stock'],
                'optional': ['count', 'on hand', 'available', 'quantity'],
                'filename_keywords': ['inventory', 'stock', 'count']
            },
            'supplier': {
                'required': ['supplier', 'cost'],
                'optional': ['vendor', 'invoice', 'purchase', 'delivery'],
                'filename_keywords': ['supplier', 'vendor', 'invoice', 'purchase']
            }
        }
        
        best_data_type = 'other'
        best_confidence = 0.0
        
        for data_type, patterns in data_type_patterns.items():
            # Check required fields
            required_matches = sum(1 for req in patterns['required'] 
                                 if any(req in col for col in columns))
            required_score = required_matches / len(patterns['required']) if patterns['required'] else 0
            
            # Check optional fields
            optional_matches = sum(1 for opt in patterns['optional'] 
                                 if any(opt in col for col in columns))
            optional_score = optional_matches / len(patterns['optional']) if patterns['optional'] else 0
            
            # Check filename
            filename_score = sum(1 for keyword in patterns['filename_keywords'] 
                               if keyword in filename_lower)
            filename_boost = min(filename_score * 0.2, 0.3)
            
            # Combined confidence
            confidence = (required_score * 0.6) + (optional_score * 0.3) + filename_boost
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_data_type = data_type
        
        # Enhanced column mapping
        column_mapping = self._create_smart_column_mapping(df.columns, best_data_type, pos_system)
        
        # Calculate overall confidence
        overall_confidence = min((best_confidence + pos_confidence) / 2, 0.95)
        
        return {
            'data_type': best_data_type,
            'pos_system': pos_system,
            'confidence': overall_confidence,
            'column_mapping': column_mapping,
            'standard_field_mapping': self._create_standard_mapping(column_mapping, df.columns),
            'business_intelligence': self._infer_business_intelligence(df, best_data_type, pos_system),
            'suggestions': self._generate_pattern_suggestions(best_data_type, pos_system, overall_confidence),
            'reasoning': f"Pattern detection: {best_data_type} from {pos_system} (confidence: {overall_confidence:.2f})"
        }
    
    def _create_smart_column_mapping(self, columns: List[str], data_type: str, pos_system: str) -> Dict:
        """Create intelligent column mapping based on data type and POS system"""
        mapping = {}
        
        # POS-specific mappings
        pos_mappings = {
            'square': {
                'gross sales': 'total_amount',
                'item name': 'item_name',
                'quantity': 'quantity',
                'tax': 'tax_amount',
                'tip': 'tip_amount'
            },
            'toast': {
                'item name': 'item_name',
                'quantity': 'quantity',
                'gross': 'total_amount',
                'net': 'net_amount'
            },
            'clover': {
                'name': 'item_name',
                'price': 'unit_price',
                'quantity': 'quantity',
                'amount': 'total_amount'
            }
        }
        
        # Apply POS-specific mapping first
        if pos_system in pos_mappings:
            for col in columns:
                col_lower = col.lower()
                for pattern, field in pos_mappings[pos_system].items():
                    if pattern in col_lower:
                        mapping[col] = field
                        break
        
        # Fill in remaining with generic patterns
        for col in columns:
            if col in mapping:
                continue
                
            col_lower = col.lower()
            
            # Generic patterns
            if any(word in col_lower for word in ['item', 'product', 'dish', 'menu']):
                mapping[col] = 'item_name'
            elif any(word in col_lower for word in ['qty', 'quantity', 'count']) and 'discount' not in col_lower:
                mapping[col] = 'quantity'
            elif any(word in col_lower for word in ['price', 'unit price']) and 'total' not in col_lower:
                mapping[col] = 'unit_price'
            elif any(word in col_lower for word in ['total', 'amount', 'revenue']) and 'tax' not in col_lower:
                mapping[col] = 'total_amount'
            elif any(word in col_lower for word in ['date']):
                mapping[col] = 'date'
            elif any(word in col_lower for word in ['time']):
                mapping[col] = 'time'
            elif any(word in col_lower for word in ['category', 'type', 'class']):
                mapping[col] = 'category'
            elif any(word in col_lower for word in ['cost', 'cogs']):
                mapping[col] = 'cost'
        
        return mapping
    
    def _create_standard_mapping(self, column_mapping: Dict, columns: List[str]) -> Dict:
        """Create standard field mapping"""
        standard_fields = {}
        
        # Reverse mapping to get column names for standard fields
        for col, field in column_mapping.items():
            if field not in standard_fields:  # Use first match
                standard_fields[field] = col
        
        return standard_fields
    
    def _infer_business_intelligence(self, df: pd.DataFrame, data_type: str, pos_system: str) -> Dict:
        """Infer business intelligence from data patterns"""
        intel = {}
        
        # Analyze price ranges if we have pricing data
        price_cols = [col for col in df.columns if any(word in col.lower() for word in ['price', 'amount', 'total'])]
        if price_cols:
            try:
                price_data = df[price_cols[0]].apply(self._safe_numeric)
                price_data = price_data[price_data > 0]  # Remove zeros
                
                if len(price_data) > 0:
                    avg_price = price_data.mean()
                    if avg_price < 10:
                        intel['price_range'] = 'budget'
                    elif avg_price < 25:
                        intel['price_range'] = 'mid_tier'
                    elif avg_price < 50:
                        intel['price_range'] = 'premium'
                    else:
                        intel['price_range'] = 'luxury'
                    
                    intel['avg_transaction_size'] = f"${avg_price:.2f}"
            except:
                pass
        
        # Analyze menu complexity
        item_cols = [col for col in df.columns if any(word in col.lower() for word in ['item', 'product', 'dish'])]
        if item_cols:
            unique_items = df[item_cols[0]].nunique()
            if unique_items < 20:
                intel['menu_complexity'] = 'simple'
            elif unique_items < 50:
                intel['menu_complexity'] = 'moderate'
            elif unique_items < 100:
                intel['menu_complexity'] = 'complex'
            else:
                intel['menu_complexity'] = 'very_complex'
        
        return intel
    
    def _generate_pattern_suggestions(self, data_type: str, pos_system: str, confidence: float) -> List[str]:
        """Generate helpful suggestions based on pattern detection"""
        suggestions = []
        
        if confidence < 0.7:
            suggestions.append("Consider adding clearer column headers for better auto-detection")
        
        if pos_system == 'unknown':
            suggestions.append("For better insights, export from your POS with standard field names")
        
        if data_type == 'sales':
            suggestions.append("Include date/time columns for trend analysis")
            suggestions.append("Add category columns for menu performance insights")
        
        return suggestions
    
    def _merge_analysis(self, pattern_analysis: Dict, ai_analysis: Dict) -> Dict:
        """Merge pattern detection with AI analysis for best results"""
        # Use AI analysis as base, enhance with pattern detection insights
        merged = ai_analysis.copy()
        
        # Keep higher confidence POS system detection
        if pattern_analysis.get('confidence', 0) > 0.8:
            merged['pos_system'] = pattern_analysis['pos_system']
        
        # Combine suggestions
        pattern_suggestions = pattern_analysis.get('suggestions', [])
        ai_suggestions = merged.get('suggestions', [])
        merged['suggestions'] = list(set(pattern_suggestions + ai_suggestions))
        
        # Boost overall confidence if pattern detection was high
        if pattern_analysis.get('confidence', 0) > 0.8:
            merged['confidence'] = min(merged.get('confidence', 0.8) + 0.1, 0.95)
        
        return merged
    
    def _claude_analysis(self, sample_data: str, filename: str) -> Dict:
        """Use Claude to analyze the data structure with enhanced intelligence"""
        prompt = f"""
        You are an expert restaurant data scientist and business intelligence analyst. Perform DEEP ANALYSIS of this restaurant data to extract ALL possible business intelligence.

        TASK: Analyze this data comprehensively and provide intelligent field mapping and business context.

        Filename: {filename}
        Data sample:
        {sample_data}

        RESPOND WITH COMPREHENSIVE JSON:
        {{
            "data_type": "sales|pos_export|inventory|supplier|accounting|catering|delivery|other",
            "pos_system": "toast|square|clover|resy|opentable|uber_eats|doordash|custom|unknown",
            "confidence": 0.95,
            "restaurant_type": "quick_service|casual_dining|fine_dining|bar|coffee_shop|catering|unknown",
            "time_period_detected": "single_day|week|month|quarter|year|unknown",
            
            "column_intelligence": {{
                "item_identifiers": ["exact column names for menu items"],
                "revenue_fields": ["exact column names for revenue/sales"],
                "quantity_fields": ["exact column names for quantities"],
                "price_fields": ["exact column names for unit prices"],
                "cost_fields": ["exact column names for costs/COGS"],
                "date_time_fields": ["exact column names for dates/times"],
                "category_fields": ["exact column names for categories"],
                "customer_fields": ["exact column names for customer data"],
                "payment_fields": ["exact column names for payment methods"],
                "location_fields": ["exact column names for locations/stores"],
                "staff_fields": ["exact column names for staff/servers"],
                "tax_fields": ["exact column names for taxes"],
                "discount_fields": ["exact column names for discounts"],
                "tip_fields": ["exact column names for tips"]
            }},
            
            "business_intelligence": {{
                "price_range": "budget|mid_tier|premium|luxury",
                "menu_complexity": "simple|moderate|complex|very_complex",
                "avg_transaction_size": "estimated from data",
                "peak_patterns_detectable": true/false,
                "seasonal_items_present": true/false,
                "delivery_vs_dine_in": "delivery_heavy|mixed|dine_in_heavy|unknown"
            }},
            
            "data_quality": {{
                "completeness": 0.85,
                "consistency_score": 0.90,
                "anomalies_detected": ["specific issues found"],
                "missing_critical_fields": ["what's missing for full analysis"]
            }},
            
            "smart_insights_possible": [
                "menu_engineering_analysis",
                "pricing_optimization",
                "peak_hour_identification", 
                "cross_sell_analysis",
                "customer_behavior_patterns",
                "operational_efficiency",
                "seasonal_trend_analysis",
                "profit_margin_optimization"
            ],
            
            "standard_field_mapping": {{
                "item_name": "exact_column_name_or_null",
                "quantity": "exact_column_name_or_null",
                "unit_price": "exact_column_name_or_null", 
                "total_amount": "exact_column_name_or_null",
                "date": "exact_column_name_or_null",
                "time": "exact_column_name_or_null",
                "category": "exact_column_name_or_null",
                "cost": "exact_column_name_or_null",
                "customer_id": "exact_column_name_or_null",
                "payment_method": "exact_column_name_or_null",
                "server": "exact_column_name_or_null",
                "location": "exact_column_name_or_null",
                "tax_amount": "exact_column_name_or_null",
                "discount_amount": "exact_column_name_or_null",
                "tip_amount": "exact_column_name_or_null"
            }},
            
            "intelligent_recommendations": [
                "specific suggestions for data optimization",
                "business insights that can be generated",
                "data collection improvements"
            ],
            
            "reasoning": "detailed explanation of analysis and business context"
        }}

        IMPORTANT: Be extremely specific with column names. If you see "Item Name", map it exactly as "Item Name", not "item_name".
        Focus on extracting MAXIMUM business intelligence from whatever data is available.
        """

        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            analysis = json.loads(response_text)
            return analysis
            
        except Exception as e:
            print(f"Claude analysis failed: {str(e)}")
            return self._fallback_analysis_from_sample(sample_data, filename)
    
    def _fallback_analysis(self, df: pd.DataFrame, filename: str) -> Dict:
        """Fallback analysis without AI"""
        columns = [col.lower() for col in df.columns]
        filename_lower = filename.lower()
        
        # Detect data type based on filename and columns
        data_type = "other"
        confidence = 0.6
        
        # Sales/POS detection
        sales_indicators = ['item', 'product', 'quantity', 'price', 'total', 'revenue', 'sales']
        sales_score = sum(1 for indicator in sales_indicators if any(indicator in col for col in columns))
        
        # Inventory detection
        inventory_indicators = ['stock', 'inventory', 'count', 'on hand', 'quantity']
        inventory_score = sum(1 for indicator in inventory_indicators if any(indicator in col for col in columns))
        
        # Supplier detection
        supplier_indicators = ['supplier', 'vendor', 'invoice', 'cost', 'purchase']
        supplier_score = sum(1 for indicator in supplier_indicators if any(indicator in col for col in columns))
        
        # Determine type
        if sales_score >= 2 or 'sales' in filename_lower or 'pos' in filename_lower:
            data_type = "sales"
            confidence = 0.8
        elif inventory_score >= 2 or 'inventory' in filename_lower or 'stock' in filename_lower:
            data_type = "inventory"
            confidence = 0.8
        elif supplier_score >= 2 or 'supplier' in filename_lower or 'invoice' in filename_lower:
            data_type = "supplier"
            confidence = 0.8
        
        # Basic column mapping
        column_mapping = {}
        standard_fields = {}
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Map common patterns
            if any(word in col_lower for word in ['item', 'product', 'dish', 'menu']):
                column_mapping[col] = 'item_name'
                standard_fields['item_name'] = col
            elif any(word in col_lower for word in ['quantity', 'qty', 'count']):
                column_mapping[col] = 'quantity'
                standard_fields['quantity'] = col
            elif any(word in col_lower for word in ['price', 'amount']) and 'total' not in col_lower:
                column_mapping[col] = 'price'
                standard_fields['price'] = col
            elif any(word in col_lower for word in ['total', 'revenue', 'sales']):
                column_mapping[col] = 'total_amount'
                standard_fields['total_amount'] = col
            elif any(word in col_lower for word in ['date', 'time']):
                column_mapping[col] = 'date'
                standard_fields['date'] = col
            elif any(word in col_lower for word in ['category', 'type', 'class']):
                column_mapping[col] = 'category'
                standard_fields['category'] = col
        
        return {
            'data_type': data_type,
            'confidence': confidence,
            'column_mapping': column_mapping,
            'standard_fields': standard_fields,
            'suggestions': [
                "Consider adding column headers if missing",
                "Ensure numeric columns contain only numbers",
                "Add date columns for time-based analysis"
            ],
            'reasoning': f"Detected as {data_type} based on column patterns and filename"
        }
    
    def _fallback_analysis_from_sample(self, sample_data: str, filename: str) -> Dict:
        """Fallback when Claude fails but we have sample data"""
        try:
            sample_info = json.loads(sample_data)
            columns = sample_info['columns']
            
            # Simple pattern matching
            data_type = "other"
            if any(word in filename.lower() for word in ['sales', 'pos', 'revenue']):
                data_type = "sales"
            elif any(word in filename.lower() for word in ['inventory', 'stock']):
                data_type = "inventory"
            elif any(word in filename.lower() for word in ['supplier', 'invoice']):
                data_type = "supplier"
            
            return {
                'data_type': data_type,
                'confidence': 0.7,
                'column_mapping': {col: col.lower().replace(' ', '_') for col in columns},
                'standard_fields': {},
                'suggestions': ["AI analysis unavailable - using basic detection"],
                'reasoning': "Fallback analysis based on filename and basic patterns"
            }
        except:
            return {
                'data_type': "other",
                'confidence': 0.5,
                'column_mapping': {},
                'standard_fields': {},
                'suggestions': ["Could not analyze data structure"],
                'reasoning': "Analysis failed - manual review needed"
            }
    
    def _process_based_on_analysis(self, df: pd.DataFrame, analysis: Dict) -> List[Dict]:
        """Process the data with enhanced intelligence extraction"""
        processed_records = []
        field_mapping = analysis.get('standard_field_mapping', {})
        
        # Extract business intelligence from analysis
        pos_system = analysis.get('pos_system', 'unknown')
        restaurant_type = analysis.get('restaurant_type', 'unknown')
        business_intel = analysis.get('business_intelligence', {})
        
        for index, row in df.iterrows():
            record = {}
            
            # Map fields based on enhanced AI analysis
            for standard_field, column_name in field_mapping.items():
                if column_name and column_name in df.columns:
                    value = row[column_name]
                    
                    if pd.isna(value):
                        record[standard_field] = None
                    else:
                        # Intelligent data cleaning and conversion
                        record[standard_field] = self._intelligent_field_processing(
                            value, standard_field, pos_system, restaurant_type
                        )
            
            # Extract temporal intelligence if date/time available
            if record.get('date') or record.get('time'):
                temporal_intel = self._extract_temporal_intelligence(record, row)
                record.update(temporal_intel)
            
            # Infer missing data using business intelligence
            record = self._infer_missing_data(record, business_intel, analysis)
            
            # Add enhanced metadata
            record['_metadata'] = {
                'pos_system': pos_system,
                'restaurant_type': restaurant_type,
                'data_confidence': analysis.get('confidence', 0.8),
                'row_index': index,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Keep original data for reference
            record['_original'] = {col: str(row[col]) if not pd.isna(row[col]) else None for col in df.columns}
            
            if record.get('item_name'):  # Only add records with item names
                processed_records.append(record)
        
        return processed_records
    
    def _intelligent_field_processing(self, value, field_type: str, pos_system: str, restaurant_type: str):
        """Intelligently process field values based on context"""
        if field_type in ['quantity', 'unit_price', 'total_amount', 'cost', 'tax_amount', 'discount_amount', 'tip_amount']:
            return self._safe_numeric(value)
        elif field_type in ['date', 'time']:
            return self._safe_date(value)
        elif field_type == 'item_name':
            # Clean and standardize item names
            cleaned_name = str(value).strip()
            # Remove common POS system prefixes/suffixes
            if pos_system == 'toast':
                cleaned_name = cleaned_name.replace('[MODIFIER]', '').strip()
            elif pos_system == 'square':
                cleaned_name = cleaned_name.replace('(Modifier)', '').strip()
            return cleaned_name
        elif field_type == 'category':
            # Standardize category names
            category = str(value).strip().title()
            # Map common variations
            category_mapping = {
                'Apps': 'Appetizers', 'Starters': 'Appetizers',
                'Mains': 'Entrees', 'Main Courses': 'Entrees',
                'Drinks': 'Beverages', 'Bevs': 'Beverages'
            }
            return category_mapping.get(category, category)
        else:
            return str(value).strip()
    
    def _extract_temporal_intelligence(self, record: Dict, row) -> Dict:
        """Extract time-based intelligence"""
        temporal_data = {}
        
        try:
            # Parse date if available
            if record.get('date'):
                date_obj = pd.to_datetime(record['date'])
                temporal_data.update({
                    'day_of_week': date_obj.weekday(),  # 0=Monday, 6=Sunday
                    'week_of_year': date_obj.isocalendar()[1],
                    'month': date_obj.month,
                    'quarter': (date_obj.month - 1) // 3 + 1,
                    'is_weekend': date_obj.weekday() >= 5
                })
            
            # Parse time if available
            if record.get('time'):
                time_obj = pd.to_datetime(record['time'])
                hour = time_obj.hour
                temporal_data.update({
                    'hour_of_day': hour,
                    'time_period': self._categorize_time_period(hour),
                    'is_peak_hour': hour in [11, 12, 13, 18, 19, 20]  # Common peak hours
                })
                
        except Exception as e:
            # If time parsing fails, continue without temporal data
            pass
        
        return temporal_data
    
    def _categorize_time_period(self, hour: int) -> str:
        """Categorize hour into business periods"""
        if 6 <= hour < 11:
            return 'breakfast'
        elif 11 <= hour < 16:
            return 'lunch'
        elif 16 <= hour < 21:
            return 'dinner'
        elif 21 <= hour < 24:
            return 'late_night'
        else:
            return 'overnight'
    
    def _infer_missing_data(self, record: Dict, business_intel: Dict, analysis: Dict) -> Dict:
        """Intelligently infer missing data using business context"""
        
        # Infer category if missing but we have item name
        if not record.get('category') and record.get('item_name'):
            record['category'] = self._infer_category_from_name(record['item_name'])
        
        # Estimate cost if missing (use 30% food cost ratio as default)
        if not record.get('cost') and record.get('unit_price'):
            record['estimated_cost'] = record['unit_price'] * 0.30
        
        # Calculate total if missing but have price and quantity
        if not record.get('total_amount') and record.get('unit_price') and record.get('quantity'):
            record['total_amount'] = record['unit_price'] * record['quantity']
        
        # Infer restaurant insights
        if business_intel:
            record['_business_context'] = {
                'price_tier': business_intel.get('price_range', 'unknown'),
                'menu_complexity': business_intel.get('menu_complexity', 'unknown'),
                'service_style': self._infer_service_style(business_intel)
            }
        
        return record
    
    def _infer_category_from_name(self, item_name: str) -> str:
        """Infer category from item name using smart matching"""
        name_lower = item_name.lower()
        
        # Enhanced category mapping
        category_keywords = {
            'appetizers': ['appetizer', 'starter', 'wings', 'nachos', 'calamari', 'bruschetta', 'sampler', 'bites'],
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
                return category.title()
        
        return 'Other'
    
    def _infer_service_style(self, business_intel: Dict) -> str:
        """Infer service style from business intelligence"""
        price_range = business_intel.get('price_range', '')
        complexity = business_intel.get('menu_complexity', '')
        
        if price_range == 'luxury' or complexity == 'very_complex':
            return 'fine_dining'
        elif price_range == 'budget' or complexity == 'simple':
            return 'quick_service'
        else:
            return 'casual_dining'
    
    def _safe_numeric(self, value) -> float:
        """Safely convert value to numeric"""
        if pd.isna(value):
            return 0.0
        
        try:
            # Clean common formatting
            str_value = str(value).replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace('%', '').strip()
            
            # Handle parentheses for negative numbers
            if str_value.startswith('(') and str_value.endswith(')'):
                str_value = '-' + str_value[1:-1]
            
            return float(str_value)
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_date(self, value) -> Optional[str]:
        """Safely convert value to date string"""
        if pd.isna(value):
            return None
        
        try:
            # Try pandas to_datetime which handles many formats
            parsed_date = pd.to_datetime(value)
            return parsed_date.strftime('%Y-%m-%d')
        except:
            # Return as string if can't parse
            return str(value)
    
    def _get_error_suggestions(self, error: str) -> List[str]:
        """Get helpful suggestions based on error"""
        suggestions = []
        
        if "empty" in error.lower():
            suggestions.append("Make sure the file contains data")
            suggestions.append("Check if you selected the correct sheet in Excel")
        
        if "encoding" in error.lower() or "decode" in error.lower():
            suggestions.append("Try saving the file as CSV UTF-8")
            suggestions.append("Ensure the file is not corrupted")
        
        if "format" in error.lower():
            suggestions.append("Supported formats: CSV, Excel (.xlsx, .xls)")
            suggestions.append("Make sure the file has proper column headers")
        
        if not suggestions:
            suggestions.append("Please check the file format and try again")
            suggestions.append("Ensure the file is not password protected")
        
        return suggestions