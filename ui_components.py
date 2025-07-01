"""
Neumorphic UI Components for Restaurant AI Max Opt
Soft, extruded design with monochromatic palette
"""

import streamlit as st
from typing import Optional, Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

class NeumorphicUI:
    """Neumorphic design system for the restaurant app"""
    
    # Color palette - soft monochromatic with subtle variations
    COLORS = {
        'background': '#E0E5EC',
        'surface': '#E0E5EC',
        'primary': '#6C7EE1',
        'primary_dark': '#5B6FD8',
        'success': '#52C41A',
        'warning': '#FAAD14',
        'danger': '#F5222D',
        'text_primary': '#2C3E50',
        'text_secondary': '#7F8C8D',
        'shadow_light': '#FFFFFF',
        'shadow_dark': '#A3B1C6'
    }
    
    @staticmethod
    def load_neumorphic_css():
        """Load the complete neumorphic CSS design system"""
        st.markdown("""
        <style>
        /* Import clean, modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Main app background */
        .stApp {
            background: #E0E5EC;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container with soft depth */
        .main {
            padding: 2rem;
            background: #E0E5EC;
        }
        
        /* Neumorphic card base */
        .neu-card {
            background: #E0E5EC;
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 
                9px 9px 16px #A3B1C6,
                -9px -9px 16px #FFFFFF;
            transition: all 0.3s ease;
        }
        
        .neu-card:hover {
            box-shadow: 
                11px 11px 18px #A3B1C6,
                -11px -11px 18px #FFFFFF;
        }
        
        /* Pressed/inset style */
        .neu-inset {
            background: #E0E5EC;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 
                inset 5px 5px 10px #A3B1C6,
                inset -5px -5px 10px #FFFFFF;
        }
        
        /* Header card with gradient accent */
        .neu-header {
            background: linear-gradient(135deg, #E0E5EC 0%, #D1D9E6 100%);
            border-radius: 25px;
            padding: 3rem;
            margin-bottom: 2rem;
            box-shadow: 
                12px 12px 20px #A3B1C6,
                -12px -12px 20px #FFFFFF;
            text-align: center;
        }
        
        .neu-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2C3E50;
            margin-bottom: 0.5rem;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }
        
        .neu-subtitle {
            font-size: 1.1rem;
            color: #7F8C8D;
            font-weight: 400;
        }
        
        /* Metric cards with soft extrusion */
        .neu-metric {
            background: #E0E5EC;
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            box-shadow: 
                8px 8px 15px #A3B1C6,
                -8px -8px 15px #FFFFFF;
            transition: transform 0.2s ease;
        }
        
        .neu-metric:hover {
            transform: translateY(-2px);
        }
        
        .neu-metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2C3E50;
            margin: 0.5rem 0;
        }
        
        .neu-metric-label {
            font-size: 0.9rem;
            color: #7F8C8D;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .neu-metric-change {
            font-size: 0.85rem;
            margin-top: 0.5rem;
            font-weight: 500;
        }
        
        .neu-metric-change.positive {
            color: #52C41A;
        }
        
        .neu-metric-change.negative {
            color: #F5222D;
        }
        
        /* Button styles */
        .neu-button {
            background: #E0E5EC;
            border: none;
            border-radius: 15px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            color: #2C3E50;
            cursor: pointer;
            box-shadow: 
                6px 6px 12px #A3B1C6,
                -6px -6px 12px #FFFFFF;
            transition: all 0.2s ease;
            display: inline-block;
            text-decoration: none;
        }
        
        .neu-button:hover {
            box-shadow: 
                8px 8px 15px #A3B1C6,
                -8px -8px 15px #FFFFFF;
        }
        
        .neu-button:active {
            box-shadow: 
                inset 3px 3px 6px #A3B1C6,
                inset -3px -3px 6px #FFFFFF;
        }
        
        .neu-button-primary {
            background: linear-gradient(135deg, #6C7EE1 0%, #5B6FD8 100%);
            color: white;
        }
        
        /* Input fields */
        .neu-input {
            background: #E0E5EC;
            border: none;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            width: 100%;
            box-shadow: 
                inset 4px 4px 8px #A3B1C6,
                inset -4px -4px 8px #FFFFFF;
            color: #2C3E50;
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        .neu-input:focus {
            outline: none;
            box-shadow: 
                inset 6px 6px 10px #A3B1C6,
                inset -6px -6px 10px #FFFFFF;
        }
        
        /* File uploader */
        .neu-upload {
            background: #E0E5EC;
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            border: 2px dashed #A3B1C6;
            box-shadow: 
                inset 2px 2px 5px #A3B1C6,
                inset -2px -2px 5px #FFFFFF;
            transition: all 0.3s ease;
        }
        
        .neu-upload:hover {
            border-color: #6C7EE1;
            box-shadow: 
                inset 3px 3px 7px #A3B1C6,
                inset -3px -3px 7px #FFFFFF;
        }
        
        /* Alert boxes */
        .neu-alert {
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .neu-alert-success {
            background: #E0E5EC;
            color: #52C41A;
            box-shadow: 
                5px 5px 10px #A3B1C6,
                -5px -5px 10px #FFFFFF,
                inset 1px 1px 2px rgba(82, 196, 26, 0.2);
        }
        
        .neu-alert-warning {
            background: #E0E5EC;
            color: #FAAD14;
            box-shadow: 
                5px 5px 10px #A3B1C6,
                -5px -5px 10px #FFFFFF,
                inset 1px 1px 2px rgba(250, 173, 20, 0.2);
        }
        
        .neu-alert-danger {
            background: #E0E5EC;
            color: #F5222D;
            box-shadow: 
                5px 5px 10px #A3B1C6,
                -5px -5px 10px #FFFFFF,
                inset 1px 1px 2px rgba(245, 34, 45, 0.2);
        }
        
        /* Progress indicator */
        .neu-progress {
            background: #E0E5EC;
            border-radius: 20px;
            height: 25px;
            box-shadow: 
                inset 4px 4px 8px #A3B1C6,
                inset -4px -4px 8px #FFFFFF;
            overflow: hidden;
            position: relative;
        }
        
        .neu-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #6C7EE1 0%, #5B6FD8 100%);
            border-radius: 20px;
            transition: width 0.3s ease;
            box-shadow: 2px 2px 4px rgba(108, 126, 225, 0.3);
        }
        
        /* Tabs */
        .neu-tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .neu-tab {
            background: #E0E5EC;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            color: #7F8C8D;
            cursor: pointer;
            box-shadow: 
                4px 4px 8px #A3B1C6,
                -4px -4px 8px #FFFFFF;
            transition: all 0.2s ease;
        }
        
        .neu-tab:hover {
            color: #2C3E50;
        }
        
        .neu-tab.active {
            color: #6C7EE1;
            box-shadow: 
                inset 2px 2px 4px #A3B1C6,
                inset -2px -2px 4px #FFFFFF;
        }
        
        /* Data preview table */
        .neu-table {
            background: #E0E5EC;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 
                6px 6px 12px #A3B1C6,
                -6px -6px 12px #FFFFFF;
        }
        
        .neu-table table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .neu-table th {
            background: linear-gradient(135deg, #E0E5EC 0%, #D1D9E6 100%);
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #2C3E50;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .neu-table td {
            padding: 1rem;
            border-top: 1px solid rgba(163, 177, 198, 0.3);
            color: #2C3E50;
        }
        
        .neu-table tr:hover {
            background: rgba(108, 126, 225, 0.05);
        }
        
        /* Icon containers */
        .neu-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 50px;
            height: 50px;
            border-radius: 15px;
            background: #E0E5EC;
            box-shadow: 
                4px 4px 8px #A3B1C6,
                -4px -4px 8px #FFFFFF;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* Insights cards */
        .neu-insight {
            background: #E0E5EC;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 
                5px 5px 10px #A3B1C6,
                -5px -5px 10px #FFFFFF;
            border-left: 4px solid #6C7EE1;
        }
        
        .neu-insight-title {
            font-weight: 600;
            color: #2C3E50;
            margin-bottom: 0.5rem;
        }
        
        .neu-insight-value {
            font-size: 1.2rem;
            color: #6C7EE1;
            font-weight: 700;
        }
        
        .neu-insight-description {
            color: #7F8C8D;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        /* Streamlit specific overrides */
        .stButton > button {
            background: #E0E5EC;
            border: none;
            border-radius: 15px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            color: #2C3E50;
            box-shadow: 
                6px 6px 12px #A3B1C6,
                -6px -6px 12px #FFFFFF;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            box-shadow: 
                8px 8px 15px #A3B1C6,
                -8px -8px 15px #FFFFFF;
        }
        
        .stButton > button:active {
            box-shadow: 
                inset 3px 3px 6px #A3B1C6,
                inset -3px -3px 6px #FFFFFF;
        }
        
        /* File uploader override */
        .stFileUploader {
            background: #E0E5EC;
            border-radius: 20px;
            padding: 2rem;
            border: 2px dashed #A3B1C6;
            box-shadow: 
                inset 2px 2px 5px #A3B1C6,
                inset -2px -2px 5px #FFFFFF;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: #D1D9E6;
        }
        
        .sidebar .sidebar-content {
            background: #D1D9E6;
        }
        
        /* Animations */
        @keyframes pulse-soft {
            0% { 
                box-shadow: 
                    6px 6px 12px #A3B1C6,
                    -6px -6px 12px #FFFFFF;
            }
            50% { 
                box-shadow: 
                    8px 8px 16px #A3B1C6,
                    -8px -8px 16px #FFFFFF;
            }
            100% { 
                box-shadow: 
                    6px 6px 12px #A3B1C6,
                    -6px -6px 12px #FFFFFF;
            }
        }
        
        .pulse {
            animation: pulse-soft 2s ease-in-out infinite;
        }
        
        /* Loading spinner */
        .neu-spinner {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #E0E5EC;
            box-shadow: 
                4px 4px 8px #A3B1C6,
                -4px -4px 8px #FFFFFF;
            position: relative;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header(title: str, subtitle: str):
        """Render neumorphic header"""
        st.markdown(f"""
        <div class="neu-header">
            <div class="neu-title">{title}</div>
            <div class="neu-subtitle">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metric_card(label: str, value: str, change: Optional[str] = None, 
                          change_type: str = "neutral", icon: Optional[str] = None):
        """Render a neumorphic metric card"""
        change_class = ""
        if change_type == "positive":
            change_class = "positive"
        elif change_type == "negative":
            change_class = "negative"
        
        icon_html = f'<div class="neu-icon">{icon}</div>' if icon else ''
        change_html = f'<div class="neu-metric-change {change_class}">{change}</div>' if change else ''
        
        st.markdown(f"""
        <div class="neu-metric">
            {icon_html}
            <div class="neu-metric-label">{label}</div>
            <div class="neu-metric-value">{value}</div>
            {change_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_card(content: str, title: Optional[str] = None):
        """Render a neumorphic card with content"""
        title_html = f'<h3 style="color: #2C3E50; margin-bottom: 1rem;">{title}</h3>' if title else ''
        
        st.markdown(f"""
        <div class="neu-card">
            {title_html}
            {content}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_alert(message: str, alert_type: str = "info"):
        """Render a neumorphic alert"""
        alert_class = f"neu-alert-{alert_type}"
        icon = {
            "success": "✅",
            "warning": "⚠️",
            "danger": "🚨",
            "info": "ℹ️"
        }.get(alert_type, "ℹ️")
        
        st.markdown(f"""
        <div class="neu-alert {alert_class}">
            {icon} {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress(progress: float, label: Optional[str] = None):
        """Render a neumorphic progress bar"""
        percentage = min(max(progress * 100, 0), 100)
        label_html = f'<div style="margin-bottom: 0.5rem; color: #7F8C8D;">{label}</div>' if label else ''
        
        st.markdown(f"""
        {label_html}
        <div class="neu-progress">
            <div class="neu-progress-bar" style="width: {percentage}%;"></div>
        </div>
        <div style="margin-top: 0.5rem; text-align: center; color: #7F8C8D; font-size: 0.9rem;">
            {percentage:.0f}%
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_insight(title: str, value: str, description: str, icon: Optional[str] = None):
        """Render an insight card"""
        icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ''
        
        st.markdown(f"""
        <div class="neu-insight">
            <div class="neu-insight-title">{icon_html}{title}</div>
            <div class="neu-insight-value">{value}</div>
            <div class="neu-insight-description">{description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_neumorphic_chart(data, chart_type: str = "line", title: str = ""):
        """Create charts with neumorphic styling"""
        
        # Base layout configuration
        layout = go.Layout(
            title=dict(
                text=title,
                font=dict(size=20, color='#2C3E50', family='Inter')
            ),
            paper_bgcolor='#E0E5EC',
            plot_bgcolor='#E0E5EC',
            font=dict(family='Inter', color='#2C3E50'),
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(
                gridcolor='rgba(163, 177, 198, 0.3)',
                zerolinecolor='rgba(163, 177, 198, 0.5)',
                tickfont=dict(size=11, color='#7F8C8D')
            ),
            yaxis=dict(
                gridcolor='rgba(163, 177, 198, 0.3)',
                zerolinecolor='rgba(163, 177, 198, 0.5)',
                tickfont=dict(size=11, color='#7F8C8D')
            ),
            hovermode='x unified'
        )
        
        if chart_type == "line":
            fig = go.Figure(layout=layout)
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data.values,
                mode='lines+markers',
                line=dict(color='#6C7EE1', width=3),
                marker=dict(size=8, color='#5B6FD8'),
                fill='tonexty',
                fillcolor='rgba(108, 126, 225, 0.1)'
            ))
        
        elif chart_type == "bar":
            fig = go.Figure(layout=layout)
            fig.add_trace(go.Bar(
                x=data.index,
                y=data.values,
                marker=dict(
                    color=data.values,
                    colorscale=[[0, '#6C7EE1'], [1, '#5B6FD8']],
                    line=dict(width=0)
                )
            ))
        
        elif chart_type == "donut":
            fig = go.Figure(layout=layout)
            fig.add_trace(go.Pie(
                labels=data.index,
                values=data.values,
                hole=0.6,
                marker=dict(
                    colors=['#6C7EE1', '#52C41A', '#FAAD14', '#F5222D', '#722ED1'],
                    line=dict(color='#E0E5EC', width=3)
                )
            ))
        
        return fig
    
    @staticmethod
    def render_file_upload_zone():
        """Render a beautiful file upload zone"""
        st.markdown("""
        <div class="neu-upload">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <div style="font-size: 1.2rem; font-weight: 600; color: #2C3E50; margin-bottom: 0.5rem;">
                Drop your restaurant data here
            </div>
            <div style="color: #7F8C8D; margin-bottom: 1rem;">
                Support for Excel, CSV, and all major POS exports
            </div>
            <div class="neu-button" style="display: inline-block; margin-top: 1rem;">
                Browse Files
            </div>
        </div>
        """, unsafe_allow_html=True)


class DataPreviewUI:
    """UI components for data preview and validation"""
    
    @staticmethod
    def render_file_preview(preview_data: Dict):
        """Render file preview with detection results"""
        
        # Detection confidence indicator
        confidence = preview_data['pos_detection']['confidence']
        confidence_color = '#52C41A' if confidence > 0.8 else '#FAAD14' if confidence > 0.6 else '#F5222D'
        
        st.markdown(f"""
        <div class="neu-card">
            <h3 style="color: #2C3E50; margin-bottom: 1.5rem;">📋 File Analysis Results</h3>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;">
                <div class="neu-inset" style="padding: 1rem; text-align: center;">
                    <div style="color: #7F8C8D; font-size: 0.85rem; margin-bottom: 0.5rem;">POS System</div>
                    <div style="color: #2C3E50; font-weight: 600; font-size: 1.1rem;">
                        {preview_data['pos_detection']['detected_system'].replace('_', ' ').title()}
                    </div>
                </div>
                
                <div class="neu-inset" style="padding: 1rem; text-align: center;">
                    <div style="color: #7F8C8D; font-size: 0.85rem; margin-bottom: 0.5rem;">Data Type</div>
                    <div style="color: #2C3E50; font-weight: 600; font-size: 1.1rem;">
                        {preview_data['pos_detection']['data_type'].title()}
                    </div>
                </div>
                
                <div class="neu-inset" style="padding: 1rem; text-align: center;">
                    <div style="color: #7F8C8D; font-size: 0.85rem; margin-bottom: 0.5rem;">Confidence</div>
                    <div style="color: {confidence_color}; font-weight: 600; font-size: 1.1rem;">
                        {confidence:.0%}
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700; color: #6C7EE1;">
                        {preview_data['file_info']['total_rows']:,}
                    </div>
                    <div style="color: #7F8C8D; font-size: 0.9rem;">Total Rows</div>
                </div>
                
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700; color: #6C7EE1;">
                        {preview_data['file_info']['total_columns']}
                    </div>
                    <div style="color: #7F8C8D; font-size: 0.9rem;">Columns</div>
                </div>
                
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 700; color: #6C7EE1;">
                        {preview_data['quality_indicators']['mapping_quality']:.0%}
                    </div>
                    <div style="color: #7F8C8D; font-size: 0.9rem;">Field Match</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_column_mapping(column_preview: Dict):
        """Render column mapping preview"""
        
        mapped_count = len(column_preview['mapping'])
        unmapped_count = len(column_preview['unmapped'])
        total_columns = mapped_count + unmapped_count
        
        st.markdown("""
        <div class="neu-card">
            <h3 style="color: #2C3E50; margin-bottom: 1.5rem;">🔗 Column Mapping</h3>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        NeumorphicUI.render_progress(
            mapped_count / total_columns if total_columns > 0 else 0,
            f"{mapped_count} of {total_columns} columns automatically mapped"
        )
        
        # Mapped columns
        if column_preview['mapping']:
            st.markdown("""
            <h4 style="color: #52C41A; margin-top: 1.5rem; margin-bottom: 1rem;">
                ✅ Mapped Columns
            </h4>
            """, unsafe_allow_html=True)
            
            for standard_field, column_name in column_preview['mapping'].items():
                st.markdown(f"""
                <div class="neu-inset" style="padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between;">
                    <span style="color: #7F8C8D;">{column_name}</span>
                    <span style="color: #6C7EE1; font-weight: 500;">→ {standard_field.replace('_', ' ').title()}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Unmapped columns
        if column_preview['unmapped']:
            st.markdown("""
            <h4 style="color: #FAAD14; margin-top: 1.5rem; margin-bottom: 1rem;">
                ⚠️ Unmapped Columns
            </h4>
            <p style="color: #7F8C8D; font-size: 0.9rem; margin-bottom: 1rem;">
                These columns couldn't be automatically mapped. They'll be included in the raw data.
            </p>
            """, unsafe_allow_html=True)
            
            for column in column_preview['unmapped']:
                st.markdown(f"""
                <div class="neu-inset" style="padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
                    <span style="color: #7F8C8D;">{column}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)