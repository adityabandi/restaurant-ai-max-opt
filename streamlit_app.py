import streamlit as st
import pandas as pd
from enhanced_excel_parser import EnhancedExcelParser
from hybrid_ai_system import SmartAnalytics
from data_warehouse import RestaurantDataWarehouse, get_sample_data
import datetime

# Helper class for data handling
class FileDataSource:
    def __init__(self, name: str, file_size: int):
        self.name = name
        self.file_size = file_size
        self.data_type = None  # Assigned after parsing
