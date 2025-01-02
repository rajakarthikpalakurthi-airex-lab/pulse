# visualization.py
import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class StreamlitPDWVisualizer:
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.data = {
            'time': [],
            'amplitude': [],
            'frequency': [],
            'pulse_width': []
        }
        self.fig = None
        self.initialize_plot()

    def initialize_plot(self):
        """Initialize the plotly figure with subplots"""
        self.fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Amplitude vs Time', 'Frequency vs Time', 'Pulse Width vs Time'),
            vertical_spacing=0.1
        )
        
        # Initialize empty traces for each subplot
        self.fig.add_trace(
            go.Scatter(x=[], y=[], mode='markers', name='Amplitude',
                      marker=dict(color='blue')),
            row=1, col=1
        )
        self.fig.add_trace(
            go.Scatter(x=[], y=[], mode='markers', name='Frequency',
                      marker=dict(color='red')),
            row=2, col=1
        )
        self.fig.add_trace(
            go.Scatter(x=[], y=[], mode='markers', name='Pulse Width',
                      marker=dict(color='green')),
            row=3, col=1
        )
        
        # Update layout
        self.fig.update_layout(
            height=800,
            showlegend=True,
            title_text="PDW Measurements"
        )
        
        # Update y-axis labels
        self.fig.update_yaxes(title_text="Amplitude (dBm)", row=1, col=1)
        self.fig.update_yaxes(title_text="Frequency (Hz)", row=2, col=1)
        self.fig.update_yaxes(title_text="Pulse Width (s)", row=3, col=1)
        
        # Update x-axis labels
        self.fig.update_xaxes(title_text="Time (s)", row=3, col=1)

    def update_data(self, pdw_data: pd.DataFrame):
        """Update visualization with new PDW data"""
        # Update data buffers
        self.data['time'] = pdw_data['Time'].tolist()[-self.max_points:]
        self.data['amplitude'] = pdw_data['Amplitude'].tolist()[-self.max_points:]
        self.data['frequency'] = pdw_data['Frequency'].tolist()[-self.max_points:]
        self.data['pulse_width'] = pdw_data['PulseWidth'].tolist()[-self.max_points:]
        
        # Update plot data
        with self.fig.batch_update():
            self.fig.data[0].x = self.data['time']
            self.fig.data[0].y = self.data['amplitude']
            self.fig.data[1].x = self.data['time']
            self.fig.data[1].y = self.data['frequency']
            self.fig.data[2].x = self.data['time']
            self.fig.data[2].y = self.data['pulse_width']

    def display(self, container):
        """Display the plot in a Streamlit container"""
        container.plotly_chart(self.fig, use_container_width=True)

def create_pdw_visualizer(container):
    """Create and return a PDW visualizer instance"""
    if 'pdw_visualizer' not in st.session_state:
        st.session_state.pdw_visualizer = StreamlitPDWVisualizer()
    return st.session_state.pdw_visualizer