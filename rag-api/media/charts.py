"""
Data Visualization

Handles chart and graph generation from data.
"""
import os
import io
from typing import Dict, List, Optional, Any
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from .storage import media_storage
from cost import CostTracker

# Initialize cost tracker
cost_tracker = CostTracker()

# Try to import plotly for interactive charts
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ChartGenerator:
    """Handles chart and graph generation"""
    
    def __init__(self):
        """Initialize chart generator"""
        pass
    
    def generate_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        options: Optional[Dict] = None,
        user_id: str = "default",
        format: str = "png"
    ) -> Dict:
        """
        Generate chart from data.
        
        Supported chart types:
        - line: Line chart
        - bar: Bar chart (vertical)
        - barh: Bar chart (horizontal)
        - pie: Pie chart
        - scatter: Scatter plot
        - area: Area chart
        - heatmap: Heatmap
        
        Args:
            chart_type: Type of chart
            data: Chart data (dict with 'x', 'y', or 'values' keys, or list of dicts)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            options: Additional chart options (colors, etc.)
            user_id: User identifier
            format: Output format (png, svg, pdf)
            
        Returns:
            Dict with chart_id and metadata
        """
        try:
            # Parse data
            df = self._parse_data(data)
            
            # Generate chart based on type
            fig = None
            
            if chart_type == "line":
                fig = self._create_line_chart(df, title, x_label, y_label, options)
            elif chart_type == "bar":
                fig = self._create_bar_chart(df, title, x_label, y_label, options)
            elif chart_type == "barh":
                fig = self._create_barh_chart(df, title, x_label, y_label, options)
            elif chart_type == "pie":
                fig = self._create_pie_chart(df, title, options)
            elif chart_type == "scatter":
                fig = self._create_scatter_chart(df, title, x_label, y_label, options)
            elif chart_type == "area":
                fig = self._create_area_chart(df, title, x_label, y_label, options)
            elif chart_type == "heatmap":
                fig = self._create_heatmap(df, title, options)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            # Save chart to bytes
            buffer = io.BytesIO()
            fig.savefig(buffer, format=format, dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_data = buffer.read()
            plt.close(fig)
            
            # Save to storage
            chart_id = media_storage.save_chart(
                chart_data,
                user_id,
                {
                    "chart_type": chart_type,
                    "title": title,
                    "x_label": x_label,
                    "y_label": y_label
                },
                format=format
            )
            
            # Minimal cost (local processing)
            cost = 0.001
            cost_tracker.update_budget(user_id, cost, "chart_generation")
            
            return {
                "chart_id": chart_id,
                "format": format,
                "cost": cost
            }
            
        except Exception as e:
            raise Exception(f"Chart generation failed: {str(e)}")
    
    def _parse_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Parse data into pandas DataFrame"""
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # Handle different data formats
            if "x" in data and "y" in data:
                return pd.DataFrame({"x": data["x"], "y": data["y"]})
            elif "values" in data:
                return pd.DataFrame(data["values"])
            else:
                return pd.DataFrame([data])
        else:
            raise ValueError("Invalid data format")
    
    def _create_line_chart(self, df: pd.DataFrame, title: str, x_label: Optional[str], y_label: Optional[str], options: Optional[Dict]) -> plt.Figure:
        """Create line chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_col = df.columns[0]
        y_cols = df.columns[1:] if len(df.columns) > 1 else [df.columns[0]]
        
        for y_col in y_cols:
            ax.plot(df[x_col], df[y_col], marker='o', label=y_col)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        if len(y_cols) > 1:
            ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def _create_bar_chart(self, df: pd.DataFrame, title: str, x_label: Optional[str], y_label: Optional[str], options: Optional[Dict]) -> plt.Figure:
        """Create bar chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_col = df.columns[0]
        y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        ax.bar(df[x_col], df[y_col])
        ax.set_title(title, fontsize=14, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        
        return fig
    
    def _create_barh_chart(self, df: pd.DataFrame, title: str, x_label: Optional[str], y_label: Optional[str], options: Optional[Dict]) -> plt.Figure:
        """Create horizontal bar chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_col = df.columns[0]
        y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        ax.barh(df[x_col], df[y_col])
        ax.set_title(title, fontsize=14, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        ax.grid(True, alpha=0.3, axis='x')
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, title: str, options: Optional[Dict]) -> plt.Figure:
        """Create pie chart"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels_col = df.columns[0]
        values_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        ax.pie(df[values_col], labels=df[labels_col], autopct='%1.1f%%', startangle=90)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame, title: str, x_label: Optional[str], y_label: Optional[str], options: Optional[Dict]) -> plt.Figure:
        """Create scatter plot"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_col = df.columns[0]
        y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        ax.scatter(df[x_col], df[y_col], alpha=0.6)
        ax.set_title(title, fontsize=14, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def _create_area_chart(self, df: pd.DataFrame, title: str, x_label: Optional[str], y_label: Optional[str], options: Optional[Dict]) -> plt.Figure:
        """Create area chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_col = df.columns[0]
        y_cols = df.columns[1:] if len(df.columns) > 1 else [df.columns[0]]
        
        for y_col in y_cols:
            ax.fill_between(df[x_col], df[y_col], alpha=0.5, label=y_col)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        if len(y_cols) > 1:
            ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def _create_heatmap(self, df: pd.DataFrame, title: str, options: Optional[Dict]) -> plt.Figure:
        """Create heatmap"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Convert to numeric if needed
        numeric_df = df.select_dtypes(include=['number'])
        
        im = ax.imshow(numeric_df.values, cmap='viridis', aspect='auto')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(numeric_df.columns)))
        ax.set_xticklabels(numeric_df.columns, rotation=45, ha='right')
        ax.set_yticks(range(len(numeric_df)))
        ax.set_yticklabels(numeric_df.index)
        plt.colorbar(im, ax=ax)
        
        return fig


# Global chart generator instance
chart_generator = ChartGenerator()

