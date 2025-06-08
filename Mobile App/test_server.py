#!/usr/bin/env python3
"""
Test script to verify the Raspberry Pi server is working correctly.
Sends sample sensor data to test the server endpoints.

Usage:
python3 test_server.py [server_ip]

If no IP is provided, defaults to localhost (127.0.0.1)
"""

import requests
import json
import sys
from datetime import datetime
import time

def test_server(server_ip="127.0.0.1", port=5000):
    """Test the sensor data server"""
    base_url = f"http://{server_ip}:{port}"
    
    print(f"Testing IoT Sensor Data Server at {base_url}")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Send sample sensor data
    print("\n2. Testing sensor data endpoint...")
    sample_data = {
        "timestamp": datetime.now().isoformat() + "Z",
        "accelerometer": {"x": 0.1, "y": 0.2, "z": 9.8},
        "gyroscope": {"x": 0.01, "y": 0.02, "z": 0.03},
        "location": {"latitude": 40.7128, "longitude": -74.0060, "altitude": 10, "speed": 0},
        "deviceId": "TestDevice_12345"
    }
    
    try:
        response = requests.post(
            f"{base_url}/sensor_data",
            json=sample_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Sensor data submission passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Sensor data submission failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Sensor data submission failed: {e}")
        return False
    
    # Test 3: Get recent data
    print("\n3. Testing recent data endpoint...")
    try:
        response = requests.get(f"{base_url}/recent_data?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Recent data retrieval passed")
            print(f"   Total readings: {data['total_count']}")
            print(f"   Returned readings: {data['returned_count']}")
        else:
            print(f"❌ Recent data retrieval failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Recent data retrieval failed: {e}")
    
    # Test 4: Get statistics
    print("\n4. Testing statistics endpoint...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistics retrieval passed")
            print(f"   Total readings: {stats['total_readings']}")
            print(f"   Devices: {stats['devices']}")
            print(f"   Latest timestamp: {stats['latest_timestamp']}")
        else:
            print(f"❌ Statistics retrieval failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics retrieval failed: {e}")
    
    # Test 5: Send multiple data points
    print("\n5. Testing multiple data submissions...")
    for i in range(3):
        test_data = {
            "timestamp": datetime.now().isoformat() + "Z",
            "accelerometer": {"x": 0.1 + i * 0.1, "y": 0.2 + i * 0.1, "z": 9.8 + i * 0.1},
            "gyroscope": {"x": 0.01 + i * 0.01, "y": 0.02 + i * 0.01, "z": 0.03 + i * 0.01},
            "location": {"latitude": 40.7128 + i * 0.001, "longitude": -74.0060 + i * 0.001, "altitude": 10 + i, "speed": i},
            "deviceId": f"TestDevice_{12345 + i}"
        }
        
        try:
            response = requests.post(f"{base_url}/sensor_data", json=test_data, timeout=5)
            if response.status_code == 200:
                print(f"✅ Data point {i+1} submitted successfully")
            else:
                print(f"❌ Data point {i+1} failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ Data point {i+1} failed: {e}")
        
        time.sleep(0.5)  # Small delay between submissions
    
    print("\n" + "=" * 50)
    print("🎉 Server testing completed!")
    print(f"📊 Access web interface at: {base_url}/")
    return True

def main():
    """Main function"""
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = "127.0.0.1"
    
    print("IoT Sensor Data Server Test Script")
    print("=" * 50)
    print(f"Target server: {server_ip}:5000")
    print("Make sure the server is running before starting this test!")
    print("")
    
    # Wait for user confirmation
    input("Press Enter to start testing...")
    
    test_server(server_ip)

if __name__ == "__main__":
    main() 