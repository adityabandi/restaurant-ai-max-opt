import pandas as pd
import io
import json
import os
from typing import Dict, List, Tuple
from thefuzz import fuzz

class AIExcelParser:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.ai_client_initialized = False
        if self.openrouter_api_key:
            self.initialize_ai_client()

    def initialize_ai_client(self):
        # Simulate AI client initialization (replace with actual API client setup)
        self.ai_client_initialized = True
        print("Mock OpenRouter AI client initialized")

    def parse_file(self, file_contents: bytes, filename: str) -> Dict:
        try:
            # Optimized parsing using native Pandas capabilities
            df = self._load_file(file_contents, filename)

            # File analysis through pattern detection
            file_analysis = self._smart_pattern_detection(df, filename)

            # Post-processing with native Python
            processed_data = df.to_dict(orient="records")

            return {
                "success": True,
                "data_type": file_analysis["data_type"],
                "columns_mapped": file_analysis["column_mapping"],
                "rows_processed": len(processed_data),
                "processed_data": processed_data,
                "ai_confidence": file_analysis.get("confidence", 0.85),
                "suggestions": file_analysis.get("suggestions", []),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "suggestions": self._get_error_suggestions(str(e)),
            }

    def _load_file(self, file_contents: bytes, filename: str):
        # Native parser with auto-detect + repaired CSV handling
        try:
            if filename.endswith((".csv", ".txt")):
                df = pd.read_csv(io.BytesIO(file_contents))
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(file_contents))
            else:
                raise ValueError("Unsupported file type")

            # Automated data cleaning
            return self._clean_dataframe(df)

        except pd.errors.EmptyDataError:
            raise Exception("Empty file detected")
        except Exception as e:
            if filename.endswith((".csv", ".txt")):
                # Repair corrupted CSV files (replace bad chars)
                try:
                    cleaned_data = file_contents.decode("utf-8", "ignore")
                    df = pd.read_csv(io.StringIO(cleaned_data))
                    return self._clean_dataframe(df)
                except:
                    pass

            raise Exception(f"Failed reading {filename}: {e}")

    def _clean_dataframe(self, df):
        # Standard DataFrame cleansing
        df = df.dropna(how="all").dropna(axis=1, how="all")
        df.columns = [col.strip() for col in df.columns]
        df = df.reset_index(drop=True)
        return df

    def _smart_pattern_detection(self, df: pd.DataFrame, filename: str):
        columns = [col.lower() for col in df.columns]
        filename_lower = filename.lower()

        # POS system patterns (simplified example)
        pos_patterns = {
            "square": ["gross sales", "net sales", "tax", "tip", "fees", "item name"],
            "toast": ["item", "quantity", "gross", "discount", "net"],
            "clover": ["name", "price", "amount", "tax"],
        }

        pos_system = "unknown"
        pos_confidence = 0.0

        for system, patterns in pos_patterns.items():
            matches = sum(pattern in columns for pattern in patterns)
            confidence = matches / len(patterns)
            if confidence > pos_confidence:
                pos_confidence = confidence
                pos_system = system

        # Data type assignment
        data_type_patterns = {
            "sales": ["item", "quantity", "price", "total"],
            "inventory": ["item", "stock", "quantity"],
            "accounting": ["vendor", "invoice", "total"],
        }

        best_data_type = "other"
        best_confidence = 0.0

        for data_type, required_fields in data_type_patterns.items():
            matches = sum(max(fuzz.ratio(col, pattern) for pattern in required_fields) for col in columns)
            confidence = matches / (len(required_fields) * 100)
            if confidence > best_confidence:
                best_confidence = confidence
                best_data_type = data_type

        # Column mapping (simplified)
        column_mapping = {
            col: "item_name" if "item" in col else "quantity"
            for col in df.columns
        }

        return {
            "data_type": best_data_type,
            "pos_system": pos_system,
            "confidence": pos_confidence + 0.1,  # Adjust per AI model
            "column_mapping": column_mapping,
        }

    def _get_error_suggestions(self, error):
        suggestions = [
            "Check file format (.csv/.xlsx)",
            "Verify column headers match required fields",
            "Ensure data is properly encoded",
        ]
        return suggestions
