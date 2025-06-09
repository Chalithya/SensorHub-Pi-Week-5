import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time

st.set_page_config(page_title="2D Sensor Dashboard", layout="wide")
st.title("📈 Real-Time 2D Sensor Data Visualization with Axis Selection")

DATA_FILE = "preprocessed_sensor_data.csv"
REFRESH_EVERY = 5  # seconds
NUM_POINTS = 100   # number of recent data points to show

# Available axis options
accel_options = ['accel_x', 'accel_y', 'accel_z']
gyro_options = ['gyro_x', 'gyro_y', 'gyro_z']

# Axis selection UI
col1, col2 = st.columns(2)
with col1:
    selected_accel = st.selectbox("Select Accelerometer Axis", accel_options, index=0, key="accel_axis")
with col2:
    selected_gyro = st.selectbox("Select Gyroscope Axis", gyro_options, index=0, key="gyro_axis")

# Auto-refreshable section
placeholder = st.empty()

while True:
    if not os.path.exists(DATA_FILE):
        st.error("CSV file not found.")
        break

    df = pd.read_csv(DATA_FILE).tail(NUM_POINTS)

    with placeholder.container():
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Accelerometer - {selected_accel.upper()}")
            fig_accel = px.line(df, y=selected_accel, title=f'{selected_accel.upper()} over Time')
            st.plotly_chart(fig_accel, use_container_width=True, key="accel_plot")

        with col2:
            st.subheader(f"Gyroscope - {selected_gyro.upper()}")
            fig_gyro = px.line(df, y=selected_gyro, title=f'{selected_gyro.upper()} over Time')
            st.plotly_chart(fig_gyro, use_container_width=True, key="gyro_plot")

    time.sleep(REFRESH_EVERY)
