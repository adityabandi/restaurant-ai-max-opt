import pandas as pd
import io
import json
import re
from typing import Dict, List, Tuple, Optional, Any
import anthropic
import os
from datetime import datetime
import chardet
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

class EnhancedExcelParser:
    """Next-generation Excel/CSV parser with advanced POS detection and intelligent data processing"""
    
    # Comprehensive POS patterns database
    POS_PATTERNS = {
        'square': {
            'identifiers': ['square', 'sq ', 'square for restaurants'],
            'columns': {
                'required': ['gross sales', 'net sales', 'item'],
                'optional': ['tax', 'tip', 'fees', 'discount', 'modifier', 'category', 'device', 'card brand'],
                'date_formats': ['Date', 'Time', 'Timezone']
            },
            'file_patterns': ['square_items', 'square_transactions', 'items-', 'transactions-'],
            'confidence_boost': 0.15
        },
        'toast': {
            'identifiers': ['toast', 'toasttab', 'toast pos'],
            'columns': {
                'required': ['item', 'quantity', 'gross'],
                'optional': ['net', 'void', 'comp', 'promo', 'server', 'table', 'check'],
                'date_formats': ['Date', 'Time', 'Order Date']
            },
            'file_patterns': ['toast_', 'menu_items', 'sales_summary'],
            'confidence_boost': 0.15
        },
        'clover': {
            'identifiers': ['clover', 'clover pos'],
            'columns': {
                'required': ['name', 'price', 'quantity'],
                'optional': ['amount', 'tax', 'employee', 'tender', 'note', 'revenue class'],
                'date_formats': ['Date', 'Time']
            },
            'file_patterns': ['clover_', 'orders_export', 'items_export'],
            'confidence_boost': 0.15
        },
        'lightspeed': {
            'identifiers': ['lightspeed', 'ls retail'],
            'columns': {
                'required': ['item', 'qty', 'total'],
                'optional': ['sale id', 'register', 'employee', 'customer', 'discount'],
                'date_formats': ['completed', 'sale time']
            },
            'file_patterns': ['lightspeed_', 'sales_export'],
            'confidence_boost': 0.12
        },
        'shopify': {
            'identifiers': ['shopify', 'shopify pos'],
            'columns': {
                'required': ['name', 'lineitem quantity', 'lineitem price'],
                'optional': ['email', 'financial status', 'fulfillment status', 'accepts marketing'],
                'date_formats': ['created at', 'updated at']
            },
            'file_patterns': ['orders_export', 'shopify_'],
            'confidence_boost': 0.12
        },
        'resy': {
            'identifiers': ['resy', 'reservation'],
            'columns': {
                'required': ['party size', 'date', 'time'],
                'optional': ['guest', 'venue', 'status', 'table', 'shift'],
                'date_formats': ['reservation date', 'created date']
            },
            'file_patterns': ['resy_', 'reservations_'],
            'confidence_boost': 0.10
        },
        'opentable': {
            'identifiers': ['opentable', 'open table'],
            'columns': {
                'required': ['party size', 'reservation'],
                'optional': ['guest', 'phone', 'email', 'special requests', 'tags'],
                'date_formats': ['reservation date and time']
            },
            'file_patterns': ['opentable_', 'guest_center_'],
            'confidence_boost': 0.10
        },
        'doordash': {
            'identifiers': ['doordash', 'door dash'],
            'columns': {
                'required': ['order', 'subtotal', 'delivery fee'],
                'optional': ['tip', 'total', 'customer', 'dasher', 'restaurant payout'],
                'date_formats': ['created at', 'delivered at']
            },
            'file_patterns': ['doordash_', 'delivery_report'],
            'confidence_boost': 0.12
        },
        'ubereats': {
            'identifiers': ['uber eats', 'ubereats', 'uber'],
            'columns': {
                'required': ['order', 'fare', 'uber fee'],
                'optional': ['tip', 'tax', 'total', 'restaurant payout', 'order status'],
                'date_formats': ['date', 'order date']
            },
            'file_patterns': ['uber_', 'ubereats_', 'restaurant_payment'],
            'confidence_boost': 0.12
        },
        'grubhub': {
            'identifiers': ['grubhub', 'seamless'],
            'columns': {
                'required': ['order id', 'subtotal', 'commission'],
                'optional': ['tip', 'delivery fee', 'processing fee', 'net payout'],
                'date_formats': ['order date', 'delivered date']
            },
            'file_patterns': ['grubhub_', 'seamless_', 'payout_detail'],
            'confidence_boost': 0.12
        },
        'ncr_aloha': {
            'identifiers': ['aloha', 'ncr'],
            'columns': {
                'required': ['item', 'qty', 'sales'],
                'optional': ['server', 'table', 'check', 'terminal', 'void'],
                'date_formats': ['date', 'time']
            },
            'file_patterns': ['aloha_', 'pmix', 'gnditem'],
            'confidence_boost': 0.10
        },
        'micros': {
            'identifiers': ['micros', 'oracle hospitality'],
            'columns': {
                'required': ['item', 'quantity', 'total'],
                'optional': ['employee', 'revenue center', 'order type', 'discount'],
                'date_formats': ['business date', 'transaction time']
            },
            'file_patterns': ['micros_', 'menu_item_detail'],
            'confidence_boost': 0.10
        }
    }
    
    def __init__(self):
        self.anthropic_client = None
        self._initialize_ai()
        self.encoding_cache = {}
        self.parser_stats = {
            'files_processed': 0,
            'success_rate': 0,
            'common_errors': {},
            'pos_systems_detected': {}
        }
    
    def _initialize_ai(self):
        """Initialize AI client with fallback"""
        try:
            api_key = None
            # Try Streamlit secrets first
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
                    api_key = st.secrets["ANTHROPIC_API_KEY"]
            except:
                pass
            
            # Fallback to environment variable
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY")
            
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            print(f"AI initialization skipped: {e}")
    
    def parse_file(self, file_contents: bytes, filename: str, 
                   preview_only: bool = False, 
                   auto_fix: bool = True) -> Dict:
        """Enhanced file parsing with preview mode and auto-fix capabilities"""
        
        start_time = datetime.now()
        self.parser_stats['files_processed'] += 1
        
        try:
            # Step 1: Detect encoding with confidence
            encoding_info = self._detect_encoding(file_contents)
            
            # Step 2: Initial file load with multiple strategies
            df, load_metadata = self._smart_file_load(file_contents, filename, encoding_info)
            
            if df.empty:
                raise ValueError("File appears to be empty or unreadable")
            
            # Step 3: Auto-fix common issues if enabled
            if auto_fix:
                df, fix_log = self._auto_fix_dataframe(df)
                load_metadata['fixes_applied'] = fix_log
            
            # Step 4: Enhanced POS detection
            pos_analysis = self._advanced_pos_detection(df, filename, load_metadata)
            
            # Step 5: Intelligent column mapping
            column_intelligence = self._intelligent_column_analysis(df, pos_analysis)
            
            # Step 6: If preview mode, return analysis without processing
            if preview_only:
                return self._generate_preview_response(df, pos_analysis, column_intelligence, load_metadata)
            
            # Step 7: Process data with business intelligence
            processed_data, processing_metadata = self._process_with_intelligence(
                df, pos_analysis, column_intelligence
            )
            
            # Step 8: Generate insights and recommendations
            insights = self._generate_insights(processed_data, pos_analysis, processing_metadata)
            
            # Update stats
            self.parser_stats['success_rate'] = (
                (self.parser_stats['success_rate'] * (self.parser_stats['files_processed'] - 1) + 1) 
                / self.parser_stats['files_processed']
            )
            
            if pos_analysis['pos_system'] != 'unknown':
                self.parser_stats['pos_systems_detected'][pos_analysis['pos_system']] = \
                    self.parser_stats['pos_systems_detected'].get(pos_analysis['pos_system'], 0) + 1
            
            return {
                'success': True,
                'data_type': pos_analysis['data_type'],
                'pos_system': pos_analysis['pos_system'],
                'confidence': pos_analysis['confidence'],
                'rows_processed': len(processed_data),
                'processed_data': processed_data,
                'column_mapping': column_intelligence['mapping'],
                'insights': insights,
                'metadata': {
                    'encoding': encoding_info['encoding'],
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'fixes_applied': load_metadata.get('fixes_applied', []),
                    'warnings': load_metadata.get('warnings', []),
                    'data_quality_score': self._calculate_data_quality_score(df, processed_data)
                },
                'recommendations': self._generate_recommendations(pos_analysis, insights)
            }
            
        except Exception as e:
            error_type = type(e).__name__
            self.parser_stats['common_errors'][error_type] = \
                self.parser_stats['common_errors'].get(error_type, 0) + 1
            
            return {
                'success': False,
                'error': str(e),
                'error_type': error_type,
                'suggestions': self._get_intelligent_error_suggestions(str(e), filename),
                'partial_data': self._attempt_partial_recovery(file_contents, filename)
            }
    
    def _detect_encoding(self, file_contents: bytes) -> Dict:
        """Advanced encoding detection with confidence scoring"""
        # Try chardet for automatic detection
        detector = chardet.UniversalDetector()
        
        # Feed chunks for better detection
        for i in range(0, min(len(file_contents), 10000), 1000):
            detector.feed(file_contents[i:i+1000])
            if detector.done:
                break
        detector.close()
        
        result = detector.result
        
        # Fallback encodings in order of likelihood for restaurant data
        fallback_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-16-le', 'utf-16-be']
        
        if result['confidence'] > 0.7:
            return {
                'encoding': result['encoding'],
                'confidence': result['confidence'],
                'method': 'chardet'
            }
        
        # Try fallback encodings
        for encoding in fallback_encodings:
            try:
                file_contents.decode(encoding)
                return {
                    'encoding': encoding,
                    'confidence': 0.6,
                    'method': 'fallback'
                }
            except:
                continue
        
        return {
            'encoding': 'utf-8',
            'confidence': 0.3,
            'method': 'default'
        }
    
    def _smart_file_load(self, file_contents: bytes, filename: str, encoding_info: Dict) -> Tuple[pd.DataFrame, Dict]:
        """Smart file loading with multiple strategies and detailed metadata"""
        file_extension = filename.lower().split('.')[-1]
        metadata = {
            'encoding_used': encoding_info['encoding'],
            'load_method': None,
            'warnings': [],
            'separator': None
        }
        
        # CSV loading strategies
        if file_extension == 'csv' or file_extension == 'txt':
            # Try different separators in parallel for speed
            separators = [',', ';', '\t', '|', '^']
            best_df = pd.DataFrame()
            best_score = 0
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_sep = {
                    executor.submit(self._try_csv_separator, file_contents, encoding_info['encoding'], sep): sep 
                    for sep in separators
                }
                
                for future in as_completed(future_to_sep):
                    sep = future_to_sep[future]
                    try:
                        df, score = future.result()
                        if score > best_score:
                            best_df = df
                            best_score = score
                            metadata['separator'] = sep
                    except:
                        continue
            
            if not best_df.empty:
                metadata['load_method'] = 'csv_smart_separator'
                return self._clean_dataframe(best_df), metadata
        
        # Excel loading strategies
        elif file_extension in ['xlsx', 'xls', 'xlsm', 'xlsb']:
            # Try different Excel engines
            engines = ['openpyxl', 'xlrd', 'odf', 'pyxlsb']
            
            for engine in engines:
                try:
                    # First try to read all sheets
                    excel_file = pd.ExcelFile(io.BytesIO(file_contents), engine=engine)
                    
                    # Find the most likely data sheet
                    best_sheet = None
                    best_score = 0
                    
                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name)
                        score = self._score_dataframe_quality(df)
                        
                        if score > best_score:
                            best_score = score
                            best_sheet = sheet_name
                    
                    if best_sheet:
                        df = pd.read_excel(excel_file, sheet_name=best_sheet)
                        metadata['load_method'] = f'excel_{engine}'
                        metadata['sheet_used'] = best_sheet
                        
                        if len(excel_file.sheet_names) > 1:
                            metadata['warnings'].append(
                                f"Multiple sheets found. Using '{best_sheet}'. Other sheets: {excel_file.sheet_names}"
                            )
                        
                        return self._clean_dataframe(df), metadata
                
                except Exception as e:
                    continue
        
        # Last resort - try as CSV regardless of extension
        try:
            df = pd.read_csv(io.BytesIO(file_contents), encoding=encoding_info['encoding'])
            metadata['load_method'] = 'fallback_csv'
            metadata['warnings'].append(f"Loaded {file_extension} file as CSV")
            return self._clean_dataframe(df), metadata
        except:
            pass
        
        return pd.DataFrame(), metadata
    
    def _try_csv_separator(self, file_contents: bytes, encoding: str, separator: str) -> Tuple[pd.DataFrame, float]:
        """Try loading CSV with specific separator and score the result"""
        try:
            df = pd.read_csv(
                io.BytesIO(file_contents), 
                encoding=encoding, 
                sep=separator,
                error_bad_lines=False,
                warn_bad_lines=False,
                low_memory=False
            )
            score = self._score_dataframe_quality(df)
            return df, score
        except:
            return pd.DataFrame(), 0
    
    def _score_dataframe_quality(self, df: pd.DataFrame) -> float:
        """Score dataframe quality for determining best loading strategy"""
        if df.empty:
            return 0
        
        score = 0
        
        # More columns is generally better
        score += min(len(df.columns) / 10, 1) * 0.2
        
        # More rows is better
        score += min(len(df) / 100, 1) * 0.2
        
        # Fewer unnamed columns is better
        unnamed_cols = sum(1 for col in df.columns if 'Unnamed' in str(col))
        score += (1 - unnamed_cols / len(df.columns)) * 0.2
        
        # More non-null values is better
        non_null_ratio = df.notna().sum().sum() / (len(df) * len(df.columns))
        score += non_null_ratio * 0.2
        
        # Recognizable column names boost score
        restaurant_keywords = ['item', 'product', 'quantity', 'price', 'total', 'date', 'time', 
                             'sales', 'revenue', 'order', 'customer', 'category']
        keyword_matches = sum(1 for col in df.columns 
                            for keyword in restaurant_keywords 
                            if keyword in str(col).lower())
        score += min(keyword_matches / 5, 1) * 0.2
        
        return score
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced dataframe cleaning"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Remove columns that are mostly empty (>95% null)
        null_ratios = df.isnull().sum() / len(df)
        df = df.loc[:, null_ratios < 0.95]
        
        # Clean column names
        df.columns = [str(col).strip().replace('\n', ' ').replace('\r', '') for col in df.columns]
        
        # Remove duplicate columns with same name
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Convert obvious numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric if it looks numeric
                try:
                    numeric_series = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce')
                    if numeric_series.notna().sum() > len(df) * 0.5:  # If more than 50% are valid numbers
                        df[col] = numeric_series
                except:
                    pass
        
        return df
    
    def _auto_fix_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Auto-fix common data issues"""
        fixes = []
        
        # Fix 1: Headers in wrong row
        if df.iloc[0].notna().sum() > df.columns.notna().sum():
            # First row might be the actual header
            potential_headers = df.iloc[0].fillna('').astype(str).tolist()
            if any('item' in h.lower() or 'product' in h.lower() for h in potential_headers):
                df.columns = potential_headers
                df = df[1:].reset_index(drop=True)
                fixes.append("Moved headers from first row")
        
        # Fix 2: Remove subtotal/total rows
        total_indicators = ['total', 'subtotal', 'grand total', 'sum:', 'total:']
        for col in df.columns:
            if df[col].dtype == 'object':
                mask = df[col].astype(str).str.lower().isin(total_indicators)
                if mask.any():
                    df = df[~mask]
                    fixes.append(f"Removed {mask.sum()} total/subtotal rows")
                    break
        
        # Fix 3: Split combined date-time columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                sample = df[col].dropna().astype(str).iloc[0] if len(df[col].dropna()) > 0 else ""
                if ' ' in sample and ':' in sample:  # Likely datetime
                    try:
                        datetime_series = pd.to_datetime(df[col], errors='coerce')
                        if datetime_series.notna().sum() > len(df) * 0.5:
                            df[f"{col}_date"] = datetime_series.dt.date
                            df[f"{col}_time"] = datetime_series.dt.time
                            df = df.drop(columns=[col])
                            fixes.append(f"Split {col} into date and time columns")
                    except:
                        pass
        
        # Fix 4: Standardize currency formats
        currency_symbols = ['$', '€', '£', '¥']
        for col in df.columns:
            if df[col].dtype == 'object':
                sample_str = str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else ""
                if any(symbol in sample_str for symbol in currency_symbols):
                    df[col] = df[col].astype(str).str.replace(r'[$€£¥,]', '', regex=True)
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        fixes.append(f"Cleaned currency formatting in {col}")
                    except:
                        pass
        
        return df, fixes
    
    def _advanced_pos_detection(self, df: pd.DataFrame, filename: str, metadata: Dict) -> Dict:
        """Advanced POS system detection using multiple signals"""
        
        columns_lower = [col.lower() for col in df.columns]
        filename_lower = filename.lower()
        
        # Initialize scores for each POS system
        pos_scores = {}
        
        for pos_system, patterns in self.POS_PATTERNS.items():
            score = 0.0
            matches = {
                'filename': 0,
                'identifiers': 0,
                'required_columns': 0,
                'optional_columns': 0,
                'date_formats': 0
            }
            
            # Check filename patterns
            for pattern in patterns['file_patterns']:
                if pattern in filename_lower:
                    matches['filename'] += 1
            
            # Check identifiers in filename
            for identifier in patterns['identifiers']:
                if identifier in filename_lower:
                    matches['identifiers'] += 1
            
            # Check required columns
            for req_col in patterns['columns']['required']:
                if any(req_col in col for col in columns_lower):
                    matches['required_columns'] += 1
            
            # Check optional columns
            for opt_col in patterns['columns']['optional']:
                if any(opt_col in col for col in columns_lower):
                    matches['optional_columns'] += 1
            
            # Check date format columns
            for date_col in patterns['columns']['date_formats']:
                if any(date_col.lower() in col for col in columns_lower):
                    matches['date_formats'] += 1
            
            # Calculate weighted score
            if len(patterns['columns']['required']) > 0:
                required_ratio = matches['required_columns'] / len(patterns['columns']['required'])
            else:
                required_ratio = 0
                
            optional_ratio = matches['optional_columns'] / max(len(patterns['columns']['optional']), 1)
            
            score = (
                required_ratio * 0.5 +  # Required columns most important
                optional_ratio * 0.2 +  # Optional columns help
                min(matches['filename'], 2) * 0.1 +  # Filename patterns
                min(matches['identifiers'], 2) * 0.1 +  # Identifiers in filename
                min(matches['date_formats'], 2) * 0.05  # Date formats
            )
            
            # Apply confidence boost for strong signals
            if matches['filename'] > 0 or matches['identifiers'] > 0:
                score += patterns['confidence_boost']
            
            pos_scores[pos_system] = {
                'score': score,
                'matches': matches,
                'confidence': min(score, 0.95)
            }
        
        # Find best match
        best_pos = max(pos_scores.items(), key=lambda x: x[1]['score'])
        
        # Determine data type based on columns and POS system
        data_type = self._infer_data_type(df, best_pos[0])
        
        return {
            'pos_system': best_pos[0] if best_pos[1]['score'] > 0.3 else 'unknown',
            'confidence': best_pos[1]['confidence'],
            'data_type': data_type,
            'all_scores': pos_scores,
            'detection_method': 'pattern_matching',
            'matches': best_pos[1]['matches']
        }
    
    def _infer_data_type(self, df: pd.DataFrame, pos_system: str) -> str:
        """Infer the type of data based on columns and POS system"""
        columns_lower = [col.lower() for col in df.columns]
        
        # Sales/Transaction indicators
        sales_indicators = ['item', 'product', 'quantity', 'qty', 'price', 'total', 'amount', 
                          'revenue', 'sales', 'gross', 'net', 'transaction']
        sales_score = sum(1 for indicator in sales_indicators 
                         if any(indicator in col for col in columns_lower))
        
        # Inventory indicators
        inventory_indicators = ['stock', 'inventory', 'on hand', 'available', 'reorder', 
                              'minimum', 'maximum', 'current']
        inventory_score = sum(1 for indicator in inventory_indicators 
                            if any(indicator in col for col in columns_lower))
        
        # Customer/Reservation indicators
        reservation_indicators = ['reservation', 'party', 'guest', 'covers', 'table', 
                                'booking', 'dining']
        reservation_score = sum(1 for indicator in reservation_indicators 
                              if any(indicator in col for col in columns_lower))
        
        # Delivery indicators
        delivery_indicators = ['delivery', 'driver', 'dasher', 'courier', 'pickup', 
                             'order id', 'customer address']
        delivery_score = sum(1 for indicator in delivery_indicators 
                           if any(indicator in col for col in columns_lower))
        
        # Determine type based on scores and POS system
        if pos_system in ['resy', 'opentable']:
            return 'reservations'
        elif pos_system in ['doordash', 'ubereats', 'grubhub']:
            return 'delivery'
        elif sales_score >= 3:
            return 'sales'
        elif inventory_score >= 2:
            return 'inventory'
        elif reservation_score >= 2:
            return 'reservations'
        elif delivery_score >= 2:
            return 'delivery'
        else:
            return 'other'
    
    def _intelligent_column_analysis(self, df: pd.DataFrame, pos_analysis: Dict) -> Dict:
        """Intelligent column mapping with pattern recognition"""
        
        pos_system = pos_analysis['pos_system']
        data_type = pos_analysis['data_type']
        
        # Get POS-specific mappings if available
        pos_mappings = self._get_pos_specific_mappings(pos_system)
        
        # Analyze each column
        column_analysis = {}
        standard_mapping = {}
        
        for col in df.columns:
            col_lower = col.lower()
            
            # First try POS-specific mapping
            mapped_field = None
            if pos_system in pos_mappings and col in pos_mappings[pos_system]:
                mapped_field = pos_mappings[pos_system][col]
            
            # Then try generic pattern matching
            if not mapped_field:
                mapped_field = self._match_column_pattern(col_lower, data_type)
            
            # Analyze column data type and characteristics
            col_stats = self._analyze_column_statistics(df[col])
            
            column_analysis[col] = {
                'mapped_to': mapped_field,
                'data_type': str(df[col].dtype),
                'statistics': col_stats,
                'sample_values': df[col].dropna().head(3).tolist() if len(df[col].dropna()) > 0 else []
            }
            
            if mapped_field:
                standard_mapping[mapped_field] = col
        
        return {
            'analysis': column_analysis,
            'mapping': standard_mapping,
            'unmapped_columns': [col for col in df.columns 
                               if column_analysis[col]['mapped_to'] is None],
            'quality_score': self._calculate_mapping_quality(column_analysis)
        }
    
    def _get_pos_specific_mappings(self, pos_system: str) -> Dict:
        """Get POS-specific column mappings"""
        mappings = {
            'square': {
                'Gross Sales': 'gross_amount',
                'Net Sales': 'net_amount',
                'Tax': 'tax_amount',
                'Tip': 'tip_amount',
                'Item': 'item_name',
                'Category': 'category',
                'Device Name': 'register',
                'Customer Name': 'customer_name'
            },
            'toast': {
                'Item': 'item_name',
                'Qty': 'quantity',
                'Gross': 'gross_amount',
                'Net': 'net_amount',
                'Server': 'server_name',
                'Table': 'table_number',
                'Check Number': 'check_id'
            },
            'clover': {
                'Name': 'item_name',
                'Price': 'unit_price',
                'Qty': 'quantity',
                'Amount': 'total_amount',
                'Employee': 'server_name',
                'Revenue Class': 'category'
            }
        }
        return mappings
    
    def _match_column_pattern(self, col_lower: str, data_type: str) -> Optional[str]:
        """Match column to standard field using patterns"""
        
        # Define pattern mappings by priority
        pattern_mappings = [
            # Item/Product patterns
            (['item', 'product', 'dish', 'menu item', 'sku'], 'item_name'),
            (['quantity', 'qty', 'count', 'units'], 'quantity'),
            (['price', 'unit price', 'rate'], 'unit_price'),
            (['total', 'amount', 'extended', 'line total'], 'total_amount'),
            (['gross', 'gross sales', 'gross amount'], 'gross_amount'),
            (['net', 'net sales', 'net amount'], 'net_amount'),
            
            # Financial patterns
            (['tax', 'sales tax', 'vat'], 'tax_amount'),
            (['tip', 'gratuity'], 'tip_amount'),
            (['discount', 'comp', 'promo'], 'discount_amount'),
            (['cost', 'cogs', 'unit cost'], 'cost'),
            
            # Temporal patterns
            (['date', 'transaction date', 'order date'], 'date'),
            (['time', 'transaction time', 'order time'], 'time'),
            
            # Category patterns
            (['category', 'type', 'class', 'group', 'department'], 'category'),
            (['subcategory', 'subtype', 'subclass'], 'subcategory'),
            
            # People patterns
            (['server', 'employee', 'staff', 'cashier'], 'server_name'),
            (['customer', 'guest', 'patron'], 'customer_name'),
            
            # Location patterns
            (['table', 'table number', 'table no'], 'table_number'),
            (['location', 'store', 'branch', 'outlet'], 'location'),
            
            # Payment patterns
            (['payment', 'payment method', 'tender'], 'payment_method'),
            (['card', 'card type', 'card brand'], 'card_type'),
            
            # Order patterns
            (['order', 'order id', 'transaction id', 'check'], 'order_id'),
            (['modifier', 'add on', 'extra'], 'modifier')
        ]
        
        for patterns, field_name in pattern_mappings:
            if any(pattern in col_lower for pattern in patterns):
                return field_name
        
        return None
    
    def _analyze_column_statistics(self, series: pd.Series) -> Dict:
        """Analyze column statistics for better understanding"""
        stats = {
            'null_count': series.isnull().sum(),
            'null_percentage': series.isnull().sum() / len(series) * 100,
            'unique_count': series.nunique(),
            'unique_percentage': series.nunique() / len(series) * 100
        }
        
        # Numeric statistics
        if pd.api.types.is_numeric_dtype(series):
            stats.update({
                'mean': series.mean(),
                'median': series.median(),
                'min': series.min(),
                'max': series.max(),
                'std': series.std()
            })
        
        # Date/time detection
        if series.dtype == 'object' and len(series.dropna()) > 0:
            try:
                pd.to_datetime(series.dropna().iloc[0])
                stats['likely_datetime'] = True
            except:
                stats['likely_datetime'] = False
        
        return stats
    
    def _calculate_mapping_quality(self, column_analysis: Dict) -> float:
        """Calculate quality score for column mapping"""
        total_columns = len(column_analysis)
        mapped_columns = sum(1 for col_data in column_analysis.values() 
                           if col_data['mapped_to'] is not None)
        
        important_fields = ['item_name', 'quantity', 'total_amount', 'date']
        important_mapped = sum(1 for field in important_fields 
                             if any(col_data['mapped_to'] == field 
                                   for col_data in column_analysis.values()))
        
        mapping_score = (mapped_columns / total_columns) * 0.7
        important_score = (important_mapped / len(important_fields)) * 0.3
        
        return mapping_score + important_score
    
    def _generate_preview_response(self, df: pd.DataFrame, pos_analysis: Dict, 
                                 column_intelligence: Dict, metadata: Dict) -> Dict:
        """Generate preview response for preview mode"""
        
        # Sample data for preview
        preview_rows = min(10, len(df))
        preview_data = []
        
        for idx in range(preview_rows):
            row_data = {}
            for col in df.columns:
                value = df.iloc[idx][col]
                if pd.isna(value):
                    row_data[col] = None
                else:
                    row_data[col] = str(value)
            preview_data.append(row_data)
        
        return {
            'success': True,
            'preview_mode': True,
            'file_info': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'file_size_estimate': f"{len(df) * len(df.columns) * 8 / 1024:.1f} KB"
            },
            'pos_detection': {
                'detected_system': pos_analysis['pos_system'],
                'confidence': pos_analysis['confidence'],
                'data_type': pos_analysis['data_type']
            },
            'column_preview': {
                'columns': list(df.columns),
                'mapping': column_intelligence['mapping'],
                'unmapped': column_intelligence['unmapped_columns']
            },
            'data_preview': preview_data,
            'quality_indicators': {
                'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
                'mapping_quality': column_intelligence['quality_score'],
                'data_quality': self._calculate_data_quality_score(df, None)
            },
            'warnings': metadata.get('warnings', []),
            'suggestions': self._generate_preview_suggestions(df, pos_analysis, column_intelligence)
        }
    
    def _generate_preview_suggestions(self, df: pd.DataFrame, pos_analysis: Dict, 
                                    column_intelligence: Dict) -> List[str]:
        """Generate suggestions based on preview analysis"""
        suggestions = []
        
        # POS system suggestions
        if pos_analysis['pos_system'] == 'unknown':
            suggestions.append("POS system not detected. For better analysis, ensure your file includes standard column names.")
        elif pos_analysis['confidence'] < 0.7:
            suggestions.append(f"POS system detected as {pos_analysis['pos_system']} with low confidence. Verify this is correct.")
        
        # Column mapping suggestions
        unmapped_count = len(column_intelligence['unmapped_columns'])
        if unmapped_count > 0:
            suggestions.append(f"{unmapped_count} columns couldn't be automatically mapped. Consider renaming them to standard names.")
        
        # Data quality suggestions
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        if null_percentage > 20:
            suggestions.append(f"High percentage of missing data ({null_percentage:.1f}%). Consider cleaning your data before upload.")
        
        # Data type specific suggestions
        if pos_analysis['data_type'] == 'sales':
            if 'date' not in column_intelligence['mapping']:
                suggestions.append("No date column detected. Date information is crucial for trend analysis.")
            if 'category' not in column_intelligence['mapping']:
                suggestions.append("No category column detected. Categories help with menu performance analysis.")
        
        return suggestions
    
    def _process_with_intelligence(self, df: pd.DataFrame, pos_analysis: Dict, 
                                  column_intelligence: Dict) -> Tuple[List[Dict], Dict]:
        """Process data with business intelligence"""
        
        processed_records = []
        processing_metadata = {
            'records_processed': 0,
            'records_skipped': 0,
            'enrichments_applied': [],
            'value_corrections': 0
        }
        
        mapping = column_intelligence['mapping']
        
        for idx, row in df.iterrows():
            try:
                record = {'_original_index': idx}
                
                # Map standard fields
                for standard_field, column_name in mapping.items():
                    if column_name in df.columns:
                        value = row[column_name]
                        
                        # Apply intelligent processing based on field type
                        if standard_field in ['quantity', 'unit_price', 'total_amount', 
                                            'gross_amount', 'net_amount', 'tax_amount', 
                                            'tip_amount', 'discount_amount', 'cost']:
                            value = self._process_numeric_field(value)
                        elif standard_field in ['date', 'time']:
                            value = self._process_datetime_field(value, standard_field)
                        elif standard_field == 'item_name':
                            value = self._process_item_name(value, pos_analysis['pos_system'])
                        elif standard_field == 'category':
                            value = self._process_category(value)
                        else:
                            value = self._process_text_field(value)
                        
                        record[standard_field] = value
                
                # Add enrichments
                enrichments = self._enrich_record(record, pos_analysis)
                record.update(enrichments)
                
                if enrichments:
                    processing_metadata['enrichments_applied'].extend(list(enrichments.keys()))
                
                # Validate record
                if self._validate_record(record):
                    processed_records.append(record)
                    processing_metadata['records_processed'] += 1
                else:
                    processing_metadata['records_skipped'] += 1
                    
            except Exception as e:
                processing_metadata['records_skipped'] += 1
                continue
        
        # Remove duplicate enrichment entries
        processing_metadata['enrichments_applied'] = list(set(processing_metadata['enrichments_applied']))
        
        return processed_records, processing_metadata
    
    def _process_numeric_field(self, value) -> Optional[float]:
        """Process numeric fields with intelligence"""
        if pd.isna(value):
            return None
        
        try:
            # Handle string representations
            if isinstance(value, str):
                # Remove currency symbols and formatting
                value = re.sub(r'[$€£¥,\s]', '', value)
                
                # Handle parentheses for negative numbers
                if value.startswith('(') and value.endswith(')'):
                    value = '-' + value[1:-1]
                
                # Handle percentage
                if value.endswith('%'):
                    return float(value[:-1]) / 100
            
            return float(value)
        except:
            return None
    
    def _process_datetime_field(self, value, field_type: str) -> Optional[str]:
        """Process date/time fields"""
        if pd.isna(value):
            return None
        
        try:
            # Try to parse as datetime
            dt = pd.to_datetime(value)
            
            if field_type == 'date':
                return dt.strftime('%Y-%m-%d')
            elif field_type == 'time':
                return dt.strftime('%H:%M:%S')
            else:
                return dt.isoformat()
        except:
            return str(value)
    
    def _process_item_name(self, value, pos_system: str) -> Optional[str]:
        """Process item names with POS-specific cleaning"""
        if pd.isna(value):
            return None
        
        name = str(value).strip()
        
        # POS-specific cleaning
        if pos_system == 'square':
            name = re.sub(r'\[MODIFIER\]', '', name)
            name = re.sub(r'\(Modifier\)', '', name)
        elif pos_system == 'toast':
            name = re.sub(r'^\*+', '', name)  # Remove modifier indicators
        elif pos_system == 'clover':
            name = re.sub(r'\s+\(.*?\)$', '', name)  # Remove trailing parentheses
        
        # General cleaning
        name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
        name = name.strip()
        
        return name if name else None
    
    def _process_category(self, value) -> Optional[str]:
        """Process and standardize category names"""
        if pd.isna(value):
            return None
        
        category = str(value).strip().title()
        
        # Standardize common variations
        category_mapping = {
            'Apps': 'Appetizers',
            'Starters': 'Appetizers',
            'Entree': 'Entrees',
            'Main': 'Entrees',
            'Mains': 'Entrees',
            'Beverage': 'Beverages',
            'Drinks': 'Beverages',
            'Dessert': 'Desserts',
            'Sweets': 'Desserts'
        }
        
        return category_mapping.get(category, category)
    
    def _process_text_field(self, value) -> Optional[str]:
        """Process general text fields"""
        if pd.isna(value):
            return None
        
        text = str(value).strip()
        return text if text else None
    
    def _enrich_record(self, record: Dict, pos_analysis: Dict) -> Dict:
        """Enrich record with additional calculated fields"""
        enrichments = {}
        
        # Time-based enrichments
        if record.get('date'):
            try:
                date_obj = pd.to_datetime(record['date'])
                enrichments['day_of_week'] = date_obj.day_name()
                enrichments['month'] = date_obj.month
                enrichments['year'] = date_obj.year
                enrichments['quarter'] = f"Q{(date_obj.month - 1) // 3 + 1}"
                enrichments['is_weekend'] = date_obj.weekday() >= 5
            except:
                pass
        
        if record.get('time'):
            try:
                time_str = record['time']
                hour = int(time_str.split(':')[0])
                enrichments['hour'] = hour
                enrichments['day_part'] = self._categorize_day_part(hour)
                enrichments['is_peak_hour'] = hour in [12, 13, 18, 19, 20]
            except:
                pass
        
        # Financial enrichments
        if record.get('quantity') and record.get('unit_price') and not record.get('total_amount'):
            enrichments['calculated_total'] = record['quantity'] * record['unit_price']
        
        if record.get('gross_amount') and record.get('net_amount'):
            enrichments['discount_percentage'] = (
                (record['gross_amount'] - record['net_amount']) / record['gross_amount'] * 100
                if record['gross_amount'] > 0 else 0
            )
        
        # Category inference if missing
        if not record.get('category') and record.get('item_name'):
            enrichments['inferred_category'] = self._infer_category_from_item(record['item_name'])
        
        return enrichments
    
    def _categorize_day_part(self, hour: int) -> str:
        """Categorize hour into day parts"""
        if 5 <= hour < 11:
            return 'Breakfast'
        elif 11 <= hour < 16:
            return 'Lunch'
        elif 16 <= hour < 21:
            return 'Dinner'
        elif 21 <= hour < 24:
            return 'Late Night'
        else:
            return 'Overnight'
    
    def _infer_category_from_item(self, item_name: str) -> str:
        """Infer category from item name using keywords"""
        name_lower = item_name.lower()
        
        category_keywords = {
            'Beverages': ['coffee', 'tea', 'soda', 'juice', 'water', 'beer', 'wine', 
                         'cocktail', 'drink', 'latte', 'cappuccino', 'espresso'],
            'Appetizers': ['appetizer', 'starter', 'wings', 'nachos', 'calamari', 
                          'bruschetta', 'dip', 'chips', 'fries'],
            'Salads': ['salad', 'caesar', 'greek', 'cobb', 'greens'],
            'Sandwiches': ['sandwich', 'burger', 'wrap', 'sub', 'panini', 'club'],
            'Pizza': ['pizza', 'calzone', 'flatbread'],
            'Pasta': ['pasta', 'spaghetti', 'linguine', 'fettuccine', 'penne', 
                     'ravioli', 'lasagna'],
            'Entrees': ['steak', 'chicken', 'fish', 'salmon', 'shrimp', 'beef', 
                       'pork', 'lamb'],
            'Desserts': ['dessert', 'cake', 'pie', 'ice cream', 'cookie', 'brownie',
                        'cheesecake', 'tiramisu'],
            'Breakfast': ['pancake', 'waffle', 'eggs', 'bacon', 'omelette', 'french toast']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        
        return 'Other'
    
    def _validate_record(self, record: Dict) -> bool:
        """Validate if record should be included"""
        # Must have at least item name or some identifier
        if not record.get('item_name') and not record.get('order_id'):
            return False
        
        # Should have some numeric value
        numeric_fields = ['quantity', 'total_amount', 'unit_price', 'gross_amount', 'net_amount']
        if not any(record.get(field) for field in numeric_fields):
            return False
        
        return True
    
    def _calculate_data_quality_score(self, df: pd.DataFrame, processed_data: Optional[List]) -> float:
        """Calculate overall data quality score"""
        scores = []
        
        # Completeness score
        total_cells = len(df) * len(df.columns)
        non_null_cells = df.notna().sum().sum()
        completeness = non_null_cells / total_cells if total_cells > 0 else 0
        scores.append(completeness)
        
        # Consistency score (low variance in data types per column)
        consistency_scores = []
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if numeric data is stored as strings
                numeric_count = df[col].apply(lambda x: str(x).replace('.', '').replace('-', '').isdigit() if pd.notna(x) else False).sum()
                if numeric_count > len(df) * 0.8:
                    consistency_scores.append(0.7)  # Mostly numeric but stored as string
                else:
                    consistency_scores.append(1.0)
            else:
                consistency_scores.append(1.0)
        
        scores.append(np.mean(consistency_scores))
        
        # Processing success rate
        if processed_data is not None:
            process_rate = len(processed_data) / len(df) if len(df) > 0 else 0
            scores.append(process_rate)
        
        return np.mean(scores)
    
    def _generate_insights(self, processed_data: List[Dict], pos_analysis: Dict, 
                         processing_metadata: Dict) -> Dict:
        """Generate business insights from processed data"""
        
        insights = {
            'summary': {},
            'patterns': [],
            'anomalies': [],
            'opportunities': []
        }
        
        if not processed_data:
            return insights
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(processed_data)
        
        # Summary statistics
        if 'total_amount' in df.columns:
            insights['summary']['total_revenue'] = df['total_amount'].sum()
            insights['summary']['average_transaction'] = df['total_amount'].mean()
            insights['summary']['transaction_count'] = len(df)
        
        if 'item_name' in df.columns:
            insights['summary']['unique_items'] = df['item_name'].nunique()
            
            # Top selling items
            top_items = df.groupby('item_name')['quantity'].sum().nlargest(5)
            insights['patterns'].append({
                'type': 'top_sellers',
                'description': 'Top 5 selling items by quantity',
                'data': top_items.to_dict()
            })
        
        # Time-based patterns
        if 'hour' in df.columns:
            hourly_sales = df.groupby('hour')['total_amount'].sum()
            peak_hours = hourly_sales.nlargest(3).index.tolist()
            insights['patterns'].append({
                'type': 'peak_hours',
                'description': f'Peak sales hours: {", ".join(map(str, peak_hours))}',
                'data': hourly_sales.to_dict()
            })
        
        # Category analysis
        if 'category' in df.columns or 'inferred_category' in df.columns:
            cat_col = 'category' if 'category' in df.columns else 'inferred_category'
            category_sales = df.groupby(cat_col)['total_amount'].sum()
            insights['patterns'].append({
                'type': 'category_performance',
                'description': 'Sales by category',
                'data': category_sales.to_dict()
            })
        
        # Anomaly detection
        if 'total_amount' in df.columns:
            # Find outliers using IQR
            Q1 = df['total_amount'].quantile(0.25)
            Q3 = df['total_amount'].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df['total_amount'] < (Q1 - 1.5 * IQR)) | 
                         (df['total_amount'] > (Q3 + 1.5 * IQR))]
            
            if len(outliers) > 0:
                insights['anomalies'].append({
                    'type': 'price_outliers',
                    'description': f'Found {len(outliers)} transactions with unusual amounts',
                    'count': len(outliers)
                })
        
        # Opportunities
        if 'discount_percentage' in df.columns:
            high_discount_items = df[df['discount_percentage'] > 20]['item_name'].value_counts()
            if len(high_discount_items) > 0:
                insights['opportunities'].append({
                    'type': 'discount_optimization',
                    'description': 'Items with high discount rates that may impact profitability',
                    'items': high_discount_items.head(5).to_dict()
                })
        
        return insights
    
    def _generate_recommendations(self, pos_analysis: Dict, insights: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data quality recommendations
        if pos_analysis['confidence'] < 0.7:
            recommendations.append({
                'priority': 'high',
                'category': 'data_quality',
                'title': 'Improve Data Export Quality',
                'description': 'Your POS data format was difficult to parse. Contact your POS provider for standard export options.',
                'impact': 'Better data quality will improve analysis accuracy by 30-40%'
            })
        
        # Missing data recommendations
        if 'patterns' in insights:
            pattern_types = [p['type'] for p in insights['patterns']]
            
            if 'peak_hours' not in pattern_types:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'data_completeness',
                    'title': 'Include Time Data',
                    'description': 'Your data lacks time information. This prevents peak hour analysis.',
                    'impact': 'Could optimize staffing and reduce labor costs by 10-15%'
                })
            
            if 'category_performance' not in pattern_types:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'data_completeness',
                    'title': 'Add Category Information',
                    'description': 'Item categories are missing. This limits menu performance analysis.',
                    'impact': 'Menu optimization could increase profits by 5-10%'
                })
        
        # Business recommendations based on insights
        if insights.get('summary', {}).get('average_transaction', 0) < 20:
            recommendations.append({
                'priority': 'high',
                'category': 'revenue',
                'title': 'Increase Average Transaction Value',
                'description': 'Your average transaction is below industry standards.',
                'impact': 'Upselling and bundles could increase revenue by 15-20%'
            })
        
        return recommendations
    
    def _get_intelligent_error_suggestions(self, error: str, filename: str) -> List[str]:
        """Get intelligent suggestions based on error type"""
        suggestions = []
        error_lower = error.lower()
        
        if 'empty' in error_lower:
            suggestions.extend([
                "Ensure the file contains data and is not just headers",
                "If using Excel, check that you're exporting the correct sheet",
                "Try saving as CSV format for better compatibility"
            ])
        
        elif 'encoding' in error_lower or 'decode' in error_lower or 'codec' in error_lower:
            suggestions.extend([
                "Save your file as CSV UTF-8 format",
                "If using Excel, use 'Save As' and select 'CSV UTF-8' format",
                "Remove special characters or emojis from your data"
            ])
        
        elif 'parse' in error_lower or 'format' in error_lower:
            suggestions.extend([
                "Ensure your file has clear column headers in the first row",
                "Remove any merged cells or complex formatting",
                "Check for hidden rows or columns that might interfere"
            ])
        
        # POS-specific suggestions
        pos_keywords = {
            'square': "Use Square's standard sales report export",
            'toast': "Export from Toast's reporting section as CSV",
            'clover': "Use Clover's transaction export feature",
            'shopify': "Export orders from Shopify admin panel"
        }
        
        for pos, suggestion in pos_keywords.items():
            if pos in filename.lower():
                suggestions.append(suggestion)
                break
        
        if not suggestions:
            suggestions.extend([
                "Ensure file is not corrupted or password protected",
                "Try exporting data again from your POS system",
                "Contact support with your specific POS system details"
            ])
        
        return suggestions
    
    def _attempt_partial_recovery(self, file_contents: bytes, filename: str) -> Optional[Dict]:
        """Attempt to recover partial data from failed file"""
        try:
            # Try to read first few lines as text
            text_lines = file_contents.decode('utf-8', errors='ignore').split('\n')[:10]
            
            if text_lines:
                return {
                    'preview_lines': text_lines,
                    'detected_separator': self._detect_separator(text_lines),
                    'possible_headers': text_lines[0].split(',') if ',' in text_lines[0] else None
                }
        except:
            pass
        
        return None
    
    def _detect_separator(self, lines: List[str]) -> str:
        """Detect the most likely separator"""
        separators = [',', ';', '\t', '|']
        separator_counts = {sep: 0 for sep in separators}
        
        for line in lines[:5]:  # Check first 5 lines
            for sep in separators:
                separator_counts[sep] += line.count(sep)
        
        return max(separator_counts.items(), key=lambda x: x[1])[0]