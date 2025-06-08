#!/usr/bin/env python3
"""
IoT Sensor Data Collection & Visualization Project
Loyalist College - Semester 3 IoT Course

This file implements all four required project sections:
1. Smartphone Sensor Data Collection (lines 298-336)
2. Data Processing and Visualization (lines 50-212, 385-587) 
3. Web Interface for Remote Monitoring (lines 269-292, templates/)
4. Complete system for demonstration and evaluation

Enhanced web interface with real-time analytics, interactive visualizations, and data export
"""

from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
import csv
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import socket
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
import io
import base64
from werkzeug.utils import secure_filename
import math
import zipfile
from threading import Thread
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Configuration
CSV_FILE = 'sensor_data.csv'
DB_FILE = 'sensor_data.db'
UPLOAD_FOLDER = 'uploads'
EXPORT_FOLDER = 'exports'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)
os.makedirs('static/charts', exist_ok=True)

# CSV Headers - Organized for pandas analysis
CSV_HEADERS = ['timestamp', 'device_id', 'accel_x', 'accel_y', 'accel_z', 
               'gyro_x', 'gyro_y', 'gyro_z', 'latitude', 'longitude', 
               'altitude', 'speed', 'activity']

# Column descriptions for export documentation
COLUMN_DESCRIPTIONS = {
    'timestamp': 'ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS.sssZ)',
    'device_id': 'Unique device identifier',
    'accel_x': 'Accelerometer X-axis (m/s²)',
    'accel_y': 'Accelerometer Y-axis (m/s²)', 
    'accel_z': 'Accelerometer Z-axis (m/s²)',
    'gyro_x': 'Gyroscope X-axis (rad/s)',
    'gyro_y': 'Gyroscope Y-axis (rad/s)',
    'gyro_z': 'Gyroscope Z-axis (rad/s)',
    'latitude': 'GPS Latitude (decimal degrees)',
    'longitude': 'GPS Longitude (decimal degrees)',
    'altitude': 'GPS Altitude (meters)',
    'speed': 'Speed from GPS (m/s)',
    'activity': 'Classified activity (stationary, walking, running, etc.)'
}

def get_server_ip():
    """Get the server's IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def initialize_database():
    """Initialize SQLite database for better data management"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            device_id TEXT NOT NULL,
            accel_x REAL,
            accel_y REAL,
            accel_z REAL,
            gyro_x REAL,
            gyro_y REAL,
            gyro_z REAL,
            latitude REAL,
            longitude REAL,
            altitude REAL,
            speed REAL,
            activity TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_data(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_id ON sensor_data(device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity ON sensor_data(activity)')
    
    conn.commit()
    conn.close()

def initialize_csv():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)
        print(f"📝 Created new CSV file: {CSV_FILE}")

def get_data_stats():
    """Get comprehensive statistics from the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        
        # Basic stats
        total_readings = pd.read_sql_query("SELECT COUNT(*) as count FROM sensor_data", conn).iloc[0]['count']
        unique_devices = pd.read_sql_query("SELECT COUNT(DISTINCT device_id) as count FROM sensor_data", conn).iloc[0]['count']
        
        if total_readings == 0:
            conn.close()
            return {
                "total_readings": 0,
                "unique_devices": 0,
                "latest_timestamp": "No data",
                "avg_accelerometer": {"x": 0, "y": 0, "z": 0},
                "data_size_mb": 0,
                "activity_distribution": {},
                "time_range": {"start": None, "end": None},
                "avg_speed": 0,
                "max_speed": 0
            }
        
        # Get latest timestamp
        latest_timestamp = pd.read_sql_query("SELECT timestamp FROM sensor_data ORDER BY id DESC LIMIT 1", conn).iloc[0]['timestamp']
        
        # Get averages
        df = pd.read_sql_query("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 1000", conn)  # Last 1000 records for performance
        
        avg_accel = {
            "x": float(df['accel_x'].mean()) if not df.empty else 0,
            "y": float(df['accel_y'].mean()) if not df.empty else 0,
            "z": float(df['accel_z'].mean()) if not df.empty else 0
        }
        
        # Activity distribution
        activity_dist = df['activity'].value_counts().to_dict() if not df.empty else {}
        
        # Speed stats
        avg_speed = float(df['speed'].mean()) if not df.empty else 0
        max_speed = float(df['speed'].max()) if not df.empty else 0
        
        # Time range
        time_range = {
            "start": df['timestamp'].min() if not df.empty else None,
            "end": df['timestamp'].max() if not df.empty else None
        }
        
        # File size
        file_size_mb = round(os.path.getsize(DB_FILE) / (1024 * 1024), 3) if os.path.exists(DB_FILE) else 0
        
        conn.close()
        
        return {
            "total_readings": int(total_readings),
            "unique_devices": int(unique_devices),
            "latest_timestamp": str(latest_timestamp),
            "avg_accelerometer": avg_accel,
            "data_size_mb": float(file_size_mb),
            "activity_distribution": activity_dist,
            "time_range": time_range,
            "avg_speed": avg_speed,
            "max_speed": max_speed,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"❌ Error calculating stats: {e}")
        return {
            "error": f"Stats calculation failed: {str(e)}",
            "total_readings": 0,
            "unique_devices": 0,
            "latest_timestamp": "Error",
            "avg_accelerometer": {"x": 0, "y": 0, "z": 0},
            "data_size_mb": 0
        }

def classify_activity(accel_data, gyro_data):
    """Enhanced activity classification based on sensor data"""
    accel_magnitude = np.sqrt(accel_data['x']**2 + accel_data['y']**2 + accel_data['z']**2)
    gyro_magnitude = np.sqrt(gyro_data['x']**2 + gyro_data['y']**2 + gyro_data['z']**2)
    
    if accel_magnitude > 20:
        return "running"
    elif accel_magnitude > 15:
        return "walking_fast"
    elif accel_magnitude > 12:
        return "walking"
    elif gyro_magnitude > 3:
        return "turning_fast"
    elif gyro_magnitude > 1.5:
        return "turning"
    elif accel_magnitude < 9:
        return "freefall"
    else:
        return "stationary"

def store_sensor_data(data):
    """Store sensor data in both CSV and SQLite database"""
    try:
        # Store in CSV
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                data.get('timestamp', datetime.now().isoformat()),
                data.get('device_id', 'unknown'),
                data.get('accel_x', 0),
                data.get('accel_y', 0),
                data.get('accel_z', 0),
                data.get('gyro_x', 0),
                data.get('gyro_y', 0),
                data.get('gyro_z', 0),
                data.get('latitude', 0),
                data.get('longitude', 0),
                data.get('altitude', 0),
                data.get('speed', 0),
                data.get('activity', 'unknown')
            ])
        
        # Store in database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data 
            (timestamp, device_id, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, 
             latitude, longitude, altitude, speed, activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp', datetime.now().isoformat()),
            data.get('device_id', 'unknown'),
            data.get('accel_x', 0),
            data.get('accel_y', 0),
            data.get('accel_z', 0),
            data.get('gyro_x', 0),
            data.get('gyro_y', 0),
            data.get('gyro_z', 0),
            data.get('latitude', 0),
            data.get('longitude', 0),
            data.get('altitude', 0),
            data.get('speed', 0),
            data.get('activity', 'unknown')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error storing data: {e}")
        return False

# ==================== WEB ROUTES ====================

# ========================================================================
# SECTION 3: WEB INTERFACE FOR REMOTE MONITORING
# Flask routes for web pages accessible from any device on network
# Responsive design works on laptops, tablets, and smartphones
# ========================================================================

@app.route('/')
def dashboard():
    """Enhanced main dashboard"""
    server_ip = get_server_ip()
    stats = get_data_stats()
    return render_template('dashboard.html', stats=stats, server_ip=server_ip)

@app.route('/visualizations')
def visualizations():
    """Interactive visualizations page"""
    return render_template('visualizations.html')

@app.route('/analytics')
def analytics():
    """Advanced analytics page"""
    return render_template('analytics.html')

@app.route('/data-export')
def data_export():
    """Data export and management page"""
    return render_template('data_export.html')

# ==================== API ROUTES ====================

@app.route('/api/stats')
def api_stats():
    """Get real-time statistics"""
    return jsonify(get_data_stats())

# ========================================================================
# SECTION 1: SMARTPHONE SENSOR DATA COLLECTION
# Receives sensor data from smartphone apps via HTTP POST requests
# Stores data in both CSV and SQLite database for redundancy
# ========================================================================

@app.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    """Receive sensor data from smartphone"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Enhanced activity classification
        accel_data = {
            'x': data.get('accel_x', 0),
            'y': data.get('accel_y', 0),
            'z': data.get('accel_z', 0)
        }
        gyro_data = {
            'x': data.get('gyro_x', 0),
            'y': data.get('gyro_y', 0),
            'z': data.get('gyro_z', 0)
        }
        
        data['activity'] = classify_activity(accel_data, gyro_data)
        data['timestamp'] = datetime.now().isoformat()
        
        # Store data
        if store_sensor_data(data):
            return jsonify({
                "status": "success",
                "message": "Data received and stored",
                "activity_detected": data['activity'],
                "timestamp": data['timestamp']
            }), 200
        else:
            return jsonify({"error": "Failed to store data"}), 500
            
    except Exception as e:
        print(f"❌ Error processing sensor data: {e}")
        return jsonify({"error": f"Data processing failed: {str(e)}"}), 500

@app.route('/api/data')
def api_data():
    """Get sensor data with filtering options"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        device_id = request.args.get('device_id')
        activity = request.args.get('activity')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = "SELECT * FROM sensor_data WHERE 1=1"
        params = []
        
        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)
        
        if activity:
            query += " AND activity = ?"
            params.append(activity)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return jsonify({
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================================================================
# SECTION 2: DATA PROCESSING AND VISUALIZATION  
# Creates interactive charts and visualizations using Plotly
# Processes sensor data for movement patterns, activity classification
# ========================================================================

@app.route('/api/chart/realtime')
def api_chart_realtime():
    """Generate real-time sensor chart data"""
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(
            "SELECT * FROM sensor_data ORDER BY id DESC LIMIT 50", 
            conn
        )
        conn.close()
        
        if df.empty:
            return jsonify({"error": "No data available"})
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create Plotly chart with meaningful titles
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=[
                'Accelerometer Data (Linear Acceleration)', 
                'Gyroscope Data (Angular Velocity)', 
                'GPS Speed Data'
            ],
            vertical_spacing=0.12,
            specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Accelerometer (m/s²)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['accel_x'], 
                name='Accel X-axis', 
                line=dict(color='red', width=2),
                hovertemplate='Time: %{x}<br>X-axis: %{y:.3f} m/s²<extra></extra>'
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['accel_y'], 
                name='Accel Y-axis', 
                line=dict(color='green', width=2),
                hovertemplate='Time: %{x}<br>Y-axis: %{y:.3f} m/s²<extra></extra>'
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['accel_z'], 
                name='Accel Z-axis', 
                line=dict(color='blue', width=2),
                hovertemplate='Time: %{x}<br>Z-axis: %{y:.3f} m/s²<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Gyroscope (rad/s)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['gyro_x'], 
                name='Gyro X-axis', 
                line=dict(color='orange', width=2),
                hovertemplate='Time: %{x}<br>X-rotation: %{y:.3f} rad/s<extra></extra>'
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['gyro_y'], 
                name='Gyro Y-axis', 
                line=dict(color='purple', width=2),
                hovertemplate='Time: %{x}<br>Y-rotation: %{y:.3f} rad/s<extra></extra>'
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['gyro_z'], 
                name='Gyro Z-axis', 
                line=dict(color='brown', width=2),
                hovertemplate='Time: %{x}<br>Z-rotation: %{y:.3f} rad/s<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Speed (m/s)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'], 
                y=df['speed'], 
                name='GPS Speed', 
                line=dict(color='black', width=3),
                hovertemplate='Time: %{x}<br>Speed: %{y:.2f} m/s<extra></extra>'
            ),
            row=3, col=1
        )
        
        # Update axis labels and formatting
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_yaxes(title_text="Acceleration (m/s²)", row=1, col=1)
        fig.update_yaxes(title_text="Angular Velocity (rad/s)", row=2, col=1)
        fig.update_yaxes(title_text="Speed (m/s)", row=3, col=1)
        
        # Update layout with better formatting
        fig.update_layout(
            height=900,
            title_text="Real-time Sensor Data - Motion Analysis Dashboard",
            title_x=0.5,
            title_font=dict(size=16, color='darkblue'),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(size=12),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Add grid lines for better readability
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return jsonify(json.loads(fig.to_json()))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart/activity')
def api_chart_activity():
    """Generate activity distribution chart"""
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT activity, COUNT(*) as count FROM sensor_data GROUP BY activity", conn)
        conn.close()
        
        if df.empty:
            return jsonify({"error": "No data available"})
        
        fig = px.pie(df, values='count', names='activity', title='Activity Distribution')
        fig.update_layout(height=400)
        
        return jsonify(json.loads(fig.to_json()))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart/3d_motion')
def api_chart_3d_motion():
    """Generate 3D motion visualization"""
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 100", conn)
        conn.close()
        
        if df.empty:
            return jsonify({"error": "No data available"})
        
        fig = go.Figure(data=[go.Scatter3d(
            x=df['accel_x'],
            y=df['accel_y'],
            z=df['accel_z'],
            mode='markers+lines',
            marker=dict(
                size=5,
                color=df.index,
                colorscale='Viridis',
                showscale=True
            ),
            line=dict(
                color='darkblue',
                width=2
            ),
            name='3D Motion Path'
        )])
        
        fig.update_layout(
            title='3D Accelerometer Motion Visualization',
            scene=dict(
                xaxis_title='Accel X',
                yaxis_title='Accel Y',
                zaxis_title='Accel Z'
            ),
            height=500
        )
        
        return jsonify(json.loads(fig.to_json()))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/csv')
def export_csv():
    """Export data as organized CSV/TSV for pandas analysis"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        device_id = request.args.get('device_id')
        format_type = request.args.get('format', 'csv')  # Default to CSV (comma-separated)
        include_headers = request.args.get('headers', 'true').lower() == 'true'
        
        # Build query with filters
        query = "SELECT timestamp, device_id, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, latitude, longitude, altitude, speed, activity FROM sensor_data WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)
        
        query += " ORDER BY timestamp ASC"  # Changed to ascending for chronological order
        
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return jsonify({"error": "No data found for the specified criteria"}), 404
        
        # Clean and format the data for pandas analysis
        # Round numerical values to reasonable precision
        numerical_columns = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z', 'latitude', 'longitude', 'altitude', 'speed']
        for col in numerical_columns:
            if col in df.columns:
                df[col] = df[col].round(6)  # 6 decimal places for sensor data
        
        # Ensure consistent timestamp format (ISO 8601)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Handle missing/invalid GPS coordinates
        gps_columns = ['latitude', 'longitude', 'altitude']
        for col in gps_columns:
            if col in df.columns:
                # Replace invalid coordinates (0, 0) or very large numbers with NaN
                df.loc[(df[col] == 0) | (abs(df[col]) > 180), col] = np.nan
        
        # Handle speed values (-1 typically means no GPS data)
        if 'speed' in df.columns:
            df.loc[df['speed'] < 0, 'speed'] = np.nan
        
        # Create export file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type.lower() == 'tsv':
            filename = f"sensor_data_export_{timestamp}.tsv"
            separator = '\t'
        else:
            filename = f"sensor_data_export_{timestamp}.csv"
            separator = ','
        
        filepath = os.path.join(EXPORT_FOLDER, filename)
        
        # Export with proper formatting for pandas
        df.to_csv(
            filepath, 
            index=False, 
            sep=separator,
            header=include_headers,
            float_format='%.6f',  # Consistent float formatting
            na_rep='',  # Empty string for NaN values
            date_format='%Y-%m-%dT%H:%M:%S.%fZ'
        )
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.route('/api/export/json')
def export_json():
    """Export data as JSON"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        device_id = request.args.get('device_id')
        
        query = "SELECT * FROM sensor_data WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)
        
        query += " ORDER BY timestamp DESC"
        
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Create JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sensor_data_export_{timestamp}.json"
        filepath = os.path.join(EXPORT_FOLDER, filename)
        
        df.to_json(filepath, orient='records', date_format='iso')
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_data_cleanup():
    """Background task to clean up old data"""
    while True:
        try:
            # Keep only last 30 days of data
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sensor_data WHERE timestamp < ?", (cutoff_date,))
            deleted_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_rows > 0:
                print(f"🧹 Cleaned up {deleted_rows} old records")
            
            # Sleep for 24 hours
            time.sleep(24 * 60 * 60)
            
        except Exception as e:
            print(f"❌ Error in cleanup task: {e}")
            time.sleep(60 * 60)  # Sleep for 1 hour on error

if __name__ == '__main__':
    print("🚀 Starting Enhanced IoT Sensor Data Collection Server...")
    
    # Initialize database and CSV
    initialize_database()
    initialize_csv()
    
    # Start background cleanup task
    cleanup_thread = Thread(target=run_data_cleanup, daemon=True)
    cleanup_thread.start()
    
    # Get server info
    server_ip = get_server_ip()
    port = 5000
    
    print(f"\n📱 Smartphone Sensor Data Collection Server")
    print(f"🌐 Server running at: http://{server_ip}:{port}")
    print(f"📊 Dashboard: http://{server_ip}:{port}/")
    print(f"📈 Visualizations: http://{server_ip}:{port}/visualizations")
    print(f"🔍 Analytics: http://{server_ip}:{port}/analytics")
    print(f"📁 Data export: http://{server_ip}:{port}/data-export")
    print(f"🔧 API endpoint: http://{server_ip}:{port}/api/sensor_data")
    print(f"\n✅ Ready to receive sensor data!")
    print("💡 Configure your smartphone app to send data to the API endpoint")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=True) 