# IoT Sensor Data Collection App

A React Native Expo app that collects sensor data from iOS devices and transmits it to a Raspberry Pi server. This project is designed for IoT assignments and demonstrates real-time sensor data collection, processing, and wireless transmission.

## 📱 Features

### Sensor Data Collection
- **Accelerometer**: X, Y, Z acceleration values (updated every 100ms)
- **Gyroscope**: X, Y, Z rotation rates (updated every 100ms)
- **GPS Location**: Latitude, longitude, altitude, speed (updated every 2-3 seconds)
- **Device Information**: Unique device ID and orientation
- **Activity Detection**: Automatically detects walking, running, stationary, or driving

### User Interface
- Clean, modern design with real-time sensor displays
- IP address input with validation for Raspberry Pi connection
- Large START/STOP collection buttons
- Connection status indicator (green/red dot)
- Data transmission counter
- Last successful transmission timestamp
- Current activity display

### Data Transmission
- Batches sensor readings every 1-2 seconds
- HTTP POST requests to Raspberry Pi
- Graceful network error handling
- Real-time connection status updates

## 🛠️ Requirements

### Mobile App Requirements
- **iOS Device** (iPhone/iPad) - Physical device required for sensor access
- **Expo SDK 50+**
- **Node.js 18+**
- **npm or yarn**

### Raspberry Pi Server Requirements
- **Raspberry Pi** (any model with WiFi)
- **Python 3.6+**
- **Flask** web framework
- **Network connectivity** (same WiFi network as mobile device)

## 📦 Dependencies

### React Native App
```json
{
  "expo-sensors": "^14.1.4",
  "expo-location": "^18.1.5", 
  "expo-device": "^7.1.4",
  "axios": "^1.9.0"
}
```

### Python Server
```
Flask>=2.0.0
```

## 🚀 Setup Instructions

### 1. Mobile App Setup

```bash
# Clone or navigate to project directory
cd IoTSensorApp

# Install dependencies (already done if following the creation steps)
npm install

# Start the Expo development server
npm start
# or
npx expo start
```

#### Running on iOS Device
1. Install **Expo Go** app from the App Store
2. Scan the QR code displayed in terminal/browser
3. The app will load on your device

**Note**: Physical device is required - iOS Simulator cannot access device sensors.

### 2. Raspberry Pi Server Setup

#### Option A: Direct Setup on Raspberry Pi
```bash
# Copy the server file to your Raspberry Pi
scp raspberry_pi_server.py pi@[PI_IP_ADDRESS]:~/

# SSH into Raspberry Pi
ssh pi@[PI_IP_ADDRESS]

# Install Flask
pip3 install flask

# Run the server
python3 raspberry_pi_server.py
```

#### Option B: Setup from the Project Directory
```bash
# If you have the Raspberry Pi accessible locally
python3 raspberry_pi_server.py
```

The server will start on `http://0.0.0.0:5000` and display available endpoints.

## 📊 Data Format

The app sends JSON data in the following format:

```json
{
  "timestamp": "2025-06-04T10:30:00.000Z",
  "accelerometer": {
    "x": 0.1,
    "y": 0.2, 
    "z": 9.8
  },
  "gyroscope": {
    "x": 0.01,
    "y": 0.02,
    "z": 0.03
  },
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 10,
    "speed": 0
  },
  "deviceId": "iPhone_12345"
}
```

## 🔧 Usage Instructions

### 1. Start the Raspberry Pi Server
```bash
python3 raspberry_pi_server.py
```
- Server runs on port 5000
- Note the Pi's IP address (displayed in terminal or use `hostname -I`)

### 2. Configure the Mobile App
1. Open the app on your iOS device
2. Enter the Raspberry Pi IP address (e.g., `192.168.1.100`)
3. Tap **START COLLECTION**

### 3. Monitor Data Collection
- Watch real-time sensor values update on screen
- Monitor connection status (green dot = connected)
- Check transmission counter
- Observe activity detection (stationary/walking/running/driving)

### 4. View Collected Data
Access the Raspberry Pi server endpoints:
- `http://[PI_IP]:5000/` - Web interface
- `http://[PI_IP]:5000/health` - Server health check
- `http://[PI_IP]:5000/recent_data` - Recent sensor readings
- `http://[PI_IP]:5000/stats` - Collection statistics

## 📁 Data Storage

The Raspberry Pi server stores data in two ways:

1. **In-Memory**: Last 100 readings for quick access
2. **File Storage**: Daily JSON files in `sensor_data/` directory
   - Format: `sensor_data_YYYY-MM-DD.json`
   - Each line contains one sensor reading

## 🔍 Troubleshooting

### Common Issues

**App won't connect to Pi:**
- Verify both devices are on the same WiFi network
- Check IP address is correct (use `hostname -I` on Pi)
- Ensure Pi server is running on port 5000
- Check firewall settings on Pi

**Sensors not working:**
- Use physical iOS device (not simulator)
- Grant location permissions when prompted
- Ensure app has sensor access permissions

**No GPS data:**
- Enable location services in iOS Settings
- Grant location permission to Expo Go app
- Test outdoors for better GPS signal

**Connection errors:**
- Check network connectivity
- Verify IP address format (e.g., 192.168.1.100)
- Restart both app and server

### Network Setup
Ensure both devices are on the same network:
```bash
# On Raspberry Pi, check IP
hostname -I

# Test connectivity from another device
ping [PI_IP_ADDRESS]
```

## 🎯 Activity Detection Logic

The app automatically detects user activity based on sensor data:

- **Stationary**: Low acceleration and gyroscope values
- **Walking**: Moderate movement, speed < 2 m/s
- **Running**: Higher movement, speed 2-10 m/s  
- **Driving**: High speed > 10 m/s

## 📈 Performance

- **Sensor Update Rate**: 100ms for accelerometer/gyroscope
- **GPS Update Rate**: 2-3 seconds
- **Data Transmission**: Every 1.5 seconds
- **Network Timeout**: 5 seconds
- **Data Buffer**: Latest reading per transmission

## 🔒 Security Notes

- Server accepts connections from any IP (0.0.0.0)
- No authentication implemented (suitable for local networks)
- Data transmitted in plain HTTP (not HTTPS)
- For production use, implement proper security measures

## 📝 Assignment Notes

This project demonstrates:
- **IoT Sensor Integration**: Multiple sensor types with real-time data
- **Wireless Communication**: HTTP-based data transmission
- **Data Processing**: Activity detection and sensor fusion
- **User Interface**: Clean, functional mobile app design
- **Server-Side Handling**: Data reception, validation, and storage
- **Error Handling**: Network failures and graceful degradation

## 🤝 Contributing

For educational use and IoT assignments. Feel free to extend with additional features:
- HTTPS support
- Database integration
- Data visualization
- Additional sensors
- Authentication
- Real-time charting

## 📄 License

Educational use for IoT assignments at Loyalist College. 