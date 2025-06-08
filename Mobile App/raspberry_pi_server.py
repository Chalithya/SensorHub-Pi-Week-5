#!/usr/bin/env python3
"""
Raspberry Pi Server for IoT Sensor Data Collection
This Flask server receives sensor data from the React Native app
and stores it in JSON format with timestamps.

Requirements:
- Flask
- Python 3.6+

Installation:
pip3 install flask

Usage:
python3 raspberry_pi_server.py

The server will run on http://0.0.0.0:5000
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Data storage directory
DATA_DIR = "sensor_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# In-memory storage for recent data (last 100 readings)
recent_data = []
MAX_RECENT_DATA = 100

@app.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    """
    Endpoint to receive sensor data from the React Native app
    Expected JSON format:
    {
        "timestamp": "2025-06-04T10:30:00.000Z",
        "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8},
        "gyroscope": {"x": 0.01, "y": 0.02, "z": 0.03},
        "location": {"latitude": 40.7128, "longitude": -74.0060, "altitude": 10, "speed": 0},
        "deviceId": "iPhone_12345"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Validate required fields
        required_fields = ["timestamp", "accelerometer", "gyroscope", "location", "deviceId"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add server receive timestamp
        data["server_timestamp"] = datetime.now().isoformat()
        
        # Store in recent data (in memory)
        recent_data.append(data)
        if len(recent_data) > MAX_RECENT_DATA:
            recent_data.pop(0)
        
        # Save to file (one file per day)
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{DATA_DIR}/sensor_data_{today}.json"
        
        # Append to daily file
        with open(filename, "a") as f:
            f.write(json.dumps(data) + "\n")
        
        # Log the received data
        logger.info(f"Received data from {data['deviceId']} at {data['timestamp']}")
        logger.info(f"Accelerometer: {data['accelerometer']}")
        logger.info(f"Gyroscope: {data['gyroscope']}")
        logger.info(f"Location: {data['location']}")
        
        return jsonify({
            "status": "success",
            "message": "Data received successfully",
            "timestamp": data["server_timestamp"]
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_readings": len(recent_data)
    }), 200

@app.route('/recent_data', methods=['GET'])
def get_recent_data():
    """Get recent sensor data (last 100 readings)"""
    limit = request.args.get('limit', 10, type=int)
    limited_data = recent_data[-limit:] if limit < len(recent_data) else recent_data
    
    return jsonify({
        "data": limited_data,
        "total_count": len(recent_data),
        "returned_count": len(limited_data)
    }), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about received data"""
    if not recent_data:
        return jsonify({
            "total_readings": 0,
            "devices": [],
            "latest_timestamp": None
        }), 200
    
    # Get unique device IDs
    devices = list(set(data["deviceId"] for data in recent_data))
    
    # Get latest timestamp
    latest_timestamp = max(data["timestamp"] for data in recent_data)
    
    return jsonify({
        "total_readings": len(recent_data),
        "devices": devices,
        "latest_timestamp": latest_timestamp,
        "server_time": datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Simple index page"""
    return """
    <html>
    <head><title>IoT Sensor Data Server</title></head>
    <body>
        <h1>IoT Sensor Data Server</h1>
        <p>Server is running and ready to receive sensor data.</p>
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/health">GET /health</a> - Health check</li>
            <li><a href="/recent_data">GET /recent_data</a> - Recent sensor data</li>
            <li><a href="/stats">GET /stats</a> - Data statistics</li>
            <li>POST /sensor_data - Receive sensor data (from app)</li>
        </ul>
        <h2>Current Stats:</h2>
        <p>Total readings received: {}</p>
        <p>Server time: {}</p>
    </body>
    </html>
    """.format(len(recent_data), datetime.now().isoformat())

if __name__ == '__main__':
    logger.info("Starting IoT Sensor Data Server...")
    logger.info("Endpoints available:")
    logger.info("  POST /sensor_data - Receive sensor data")
    logger.info("  GET /health - Health check")
    logger.info("  GET /recent_data - Get recent readings")
    logger.info("  GET /stats - Get statistics")
    logger.info("  GET / - Index page")
    
    # Run the server
    # Use 0.0.0.0 to accept connections from any IP address
    app.run(host='0.0.0.0', port=5000, debug=True) 