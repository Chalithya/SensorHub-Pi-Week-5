from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_option = request.form.get('sensor_type', 'Accelerometer')

    csv_path = 'preprocessed_sensor_data.csv'
    if not os.path.exists(csv_path):
        return "CSV file not found."

    df = pd.read_csv(csv_path)
    latest = df.tail(100)

    fig = go.Figure()

    if selected_option == 'Accelerometer':
        fig.add_trace(go.Scatter3d(
            x=latest['accel_x'],
            y=latest['accel_y'],
            z=latest['accel_z'],
            mode='lines+markers',
            marker=dict(size=3, color='skyblue'),
            name='Accelerometer'
        ))
        title = "3D Accelerometer Data"
    else:
        fig.add_trace(go.Scatter3d(
            x=latest['gyro_x'],
            y=latest['gyro_y'],
            z=latest['gyro_z'],
            mode='lines+markers',
            marker=dict(size=3, color='orange'),
            name='Gyroscope'
        ))
        title = "3D Gyroscope Data"

    fig.update_layout(
        height=600,
        width=1000,
        title_text=title,
        margin=dict(t=60)
    )

    plot_div = pyo.plot(fig, output_type='div')
    return render_template('index.html', plot_div=plot_div, selected_option=selected_option)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
