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
        """Load file with multiple fallback strategies"""
        file_extension = filename.lower().split('.')[-1]
        
        try:
            if file_extension == 'csv':
                # Try different encodings and separators
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        for sep in [',', ';', '\t', '|']:
                            try:
                                df = pd.read_csv(io.BytesIO(file_contents), encoding=encoding, sep=sep)
                                if len(df.columns) > 1 and len(df) > 0:
                                    return self._clean_dataframe(df)
                            except:
                                continue
                    except:
                        continue
            else:
                # Excel files
                try:
                    df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
                    return self._clean_dataframe(df)
                except:
                    # Try with different engines
                    try:
                        df = pd.read_excel(io.BytesIO(file_contents), engine=None)
                        return self._clean_dataframe(df)
                    except:
                        # Last resort - try reading as CSV
                        df = pd.read_csv(io.BytesIO(file_contents))
                        return self._clean_dataframe(df)
        
        except Exception as e:
            raise Exception(f"Could not read file: {str(e)}")
        
        raise Exception("Unable to parse file format")
    
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
        """Use AI to understand the data structure and type"""
        # Prepare sample data for AI analysis
        sample_data = self._prepare_sample_for_ai(df)
        
        if self.anthropic_client:
            return self._claude_analysis(sample_data, filename)
        else:
            return self._fallback_analysis(df, filename)
    
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
    
    def _claude_analysis(self, sample_data: str, filename: str) -> Dict:
        """Use Claude to analyze the data structure"""
        prompt = f"""
        You are an expert data analyst specializing in restaurant data. Analyze this Excel/CSV data and determine:

        1. What type of restaurant data this is (sales/pos, inventory, supplier/invoice, accounting, or other)
        2. Map the columns to standard restaurant data fields
        3. Provide confidence score (0-1)
        4. Suggest any data quality improvements

        Filename: {filename}
        Data sample:
        {sample_data}

        Respond with valid JSON in this exact format:
        {{
            "data_type": "sales|inventory|supplier|accounting|other",
            "confidence": 0.95,
            "column_mapping": {{
                "original_column_name": "standard_field_name"
            }},
            "standard_fields": {{
                "item_name": "column_name_or_null",
                "quantity": "column_name_or_null",
                "price": "column_name_or_null",
                "total_amount": "column_name_or_null",
                "date": "column_name_or_null",
                "category": "column_name_or_null"
            }},
            "suggestions": ["suggestion1", "suggestion2"],
            "reasoning": "brief explanation of analysis"
        }}

        Standard field mappings:
        - Sales data: item_name, quantity, price, total_amount, date, category
        - Inventory data: item_name, quantity, unit, cost_per_unit, location
        - Supplier data: supplier_name, item_name, quantity, unit_cost, total_cost, date
        - Accounting data: account_name, debit_amount, credit_amount, date, description
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
        """Process the data based on AI analysis"""
        processed_records = []
        column_mapping = analysis.get('column_mapping', {})
        
        for _, row in df.iterrows():
            record = {}
            
            # Map columns based on AI analysis
            for original_col, standard_field in column_mapping.items():
                if original_col in df.columns:
                    value = row[original_col]
                    
                    if pd.isna(value):
                        record[standard_field] = None
                    else:
                        # Clean and convert based on field type
                        if standard_field in ['quantity', 'price', 'total_amount', 'cost_per_unit', 'unit_cost']:
                            record[standard_field] = self._safe_numeric(value)
                        elif standard_field == 'date':
                            record[standard_field] = self._safe_date(value)
                        else:
                            record[standard_field] = str(value).strip()
            
            # Keep original data for reference
            record['_original'] = {col: str(row[col]) if not pd.isna(row[col]) else None for col in df.columns}
            
            if record:  # Only add non-empty records
                processed_records.append(record)
        
        return processed_records
    
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