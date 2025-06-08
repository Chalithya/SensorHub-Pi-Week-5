from flask import Flask, render_template, jsonify
import pandas as pd
import plotly
import plotly.graph_objs as go
import json
import threading
import time


app = Flask(__name__)
DATA_FILE = 'sensor_data_export_20250606_154020.csv'
REFRESH_INTERVAL = 5  # seconds

# Global DataFrame
df = pd.read_csv(DATA_FILE)
df = df.loc[:, df.columns != 'activity']  # Ignore 'activity' column

# You can use a background thread to reload the file for 'real-time' updates if the file updates
def data_updater():
    global df
    while True:
        df = pd.read_csv(DATA_FILE)
        df = df.loc[:, df.columns != 'activity']
        time.sleep(REFRESH_INTERVAL)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/plot_data')
def plot_data():
    plots = {}

    # Accelerometer
    accel_cols = ['accel_x', 'accel_y', 'accel_z']
    accel_data = [go.Scatter(x=df.index, y=df[col], mode='lines', name=col) for col in accel_cols if col in df.columns]
    plots['accel'] = json.dumps(accel_data, cls=plotly.utils.PlotlyJSONEncoder)

    # Gyroscope
    gyro_cols = ['gyro_x', 'gyro_y', 'gyro_z']
    gyro_data = [go.Scatter(x=df.index, y=df[col], mode='lines', name=col) for col in gyro_cols if col in df.columns]
    plots['gyro'] = json.dumps(gyro_data, cls=plotly.utils.PlotlyJSONEncoder)

    # Location
    loc_cols = ['latitude', 'longitude', 'altitude']
    loc_data = [go.Scatter(x=df.index, y=df[col], mode='lines', name=col) for col in loc_cols if col in df.columns]
    plots['location'] = json.dumps(loc_data, cls=plotly.utils.PlotlyJSONEncoder)

    # Speed
    if 'speed' in df.columns:
        speed_data = [go.Scatter(x=df.index, y=df['speed'], mode='lines', name='speed')]
        plots['speed'] = json.dumps(speed_data, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        plots['speed'] = json.dumps([])

    return jsonify(plots)
if __name__ == '__main__':
    print("About to start Flask...")
    threading.Thread(target=data_updater, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
