from flask import Flask, render_template
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json

app = Flask(__name__)

# Utility to generate all plots
def generate_static_plots(csv_file):
    df = pd.read_csv(csv_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['dt'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
    df['pitch'] = np.cumsum(df['gyro_x'] * df['dt'])
    df['roll']  = np.cumsum(df['gyro_y'] * df['dt'])
    df['yaw']   = np.cumsum(df['gyro_z'] * df['dt'])

    # Acceleration plot
    plt.figure(figsize=(10, 4))
    plt.plot(df['accel_x'], label='accel_x')
    plt.plot(df['accel_y'], label='accel_y')
    plt.plot(df['accel_z'], label='accel_z')
    plt.title("Acceleration Data")
    plt.xlabel("Time Step")
    plt.ylabel("Acceleration")
    plt.legend()
    plt.tight_layout()
    plt.savefig("static/acceleration_plot.png")
    plt.close()

    # Gyroscope plot
    plt.figure(figsize=(10, 4))
    plt.plot(df['gyro_x'], label='gyro_x')
    plt.plot(df['gyro_y'], label='gyro_y')
    plt.plot(df['gyro_z'], label='gyro_z')
    plt.title("Gyroscope Data")
    plt.xlabel("Time Step")
    plt.ylabel("Angular Velocity")
    plt.legend()
    plt.tight_layout()
    plt.savefig("static/gyroscope_plot.png")
    plt.close()

    # 3D Orientation Line Plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(df['pitch'], df['roll'], df['yaw'], color='purple')
    ax.set_title("3D Orientation Tracking: Pitch, Roll, Yaw")
    ax.set_xlabel("Pitch (X)")
    ax.set_ylabel("Roll (Y)")
    ax.set_zlabel("Yaw (Z)")
    fig.tight_layout()
    plt.savefig("static/orientation_3d_plot.png")
    plt.close()

    # Pitch/Roll/Yaw vs Time Plot
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['pitch'], label='Pitch (X)', color='blue')
    plt.plot(df['timestamp'], df['roll'], label='Roll (Y)', color='orange')
    plt.plot(df['timestamp'], df['yaw'], label='Yaw (Z)', color='green')
    plt.title("3D Orientation Tracking: Pitch, Roll, Yaw Over Time")
    plt.xlabel("Time")
    plt.ylabel("Angle (Degrees)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("static/orientation_time_plot.png")
    plt.close()

@app.route('/')
def index():
    df = pd.read_csv("sensor_data_export_20250606_154020.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['dt'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
    df['pitch'] = np.cumsum(df['gyro_x'] * df['dt'])
    df['roll']  = np.cumsum(df['gyro_y'] * df['dt'])
    df['yaw']   = np.cumsum(df['gyro_z'] * df['dt'])
    orientation_data = df[['pitch', 'roll', 'yaw']].tail(100).reset_index(drop=True).to_dict(orient='records')
    return render_template('index.html', orientation=json.dumps(orientation_data))

@app.route('/graphs')
def graphs():
    generate_static_plots("sensor_data_export_20250606_154020.csv")
    return render_template('graphs.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
