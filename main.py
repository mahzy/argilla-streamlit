import plotly.express as px
import streamlit as st
from streamlit_plotly_events import plotly_events

# Select other Plotly events by specifying kwargs
fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
selected_points = plotly_events(fig, click_event=False, hover_event=True)
st.write(selected_points)
