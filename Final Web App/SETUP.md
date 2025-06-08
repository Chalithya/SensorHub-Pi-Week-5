# IoT Sensor Data Collection & Visualization - Setup Guide

**Complete setup documentation for the IoT web application**  
*Loyalist College - Semester 3 IoT Course Project*

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Guide](#installation-guide)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Smartphone Setup](#smartphone-setup)
6. [Network Setup](#network-setup)
7. [Troubleshooting](#troubleshooting)
8. [Usage Instructions](#usage-instructions)
9. [Data Management](#data-management)
10. [API Documentation](#api-documentation)

---

## 🖥️ System Requirements

### Hardware Requirements
- **Raspberry Pi** (Model 3B+ or 4 recommended)
  - Minimum 2GB RAM
  - 16GB+ microSD card
  - Wi-Fi capability
- **Smartphone** with sensor capabilities
  - Accelerometer, Gyroscope, GPS
  - Wi-Fi connectivity
  - HTTP client app capability
- **Monitor/Display** for Raspberry Pi (optional but recommended for demos)
- **Network Access** - Wi-Fi router/access point

### Software Requirements
- **Operating System**: Raspberry Pi OS (Bullseye or newer) or any Linux distribution
- **Python**: Version 3.8 or higher
- **pip**: Python package installer
- **Git**: For version control (optional)

### Supported Client Devices
- **Web Browsers**: Chrome, Firefox, Safari, Edge
- **Devices**: Laptops, tablets, smartphones, desktop computers
- **Operating Systems**: Windows, macOS, Linux, iOS, Android

---

## 🛠️ Installation Guide

### Step 1: Prepare Your Raspberry Pi

1. **Install Raspberry Pi OS**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and essential tools
   sudo apt install python3 python3-pip python3-venv git -y
   ```

2. **Verify Python Installation**
   ```bash
   python3 --version  # Should show Python 3.8+
   pip3 --version     # Should show pip version
   ```

### Step 2: Download and Setup Project

1. **Navigate to Project Directory**
   ```bash
   cd /path/to/your/project/webapp
   # or if downloading fresh:
   # git clone [your-repository-url]
   # cd webapp
   ```

2. **Create Python Virtual Environment**
   ```bash
   # Create virtual environment
   python3 -m venv iot-env
   
   # Activate virtual environment
   source iot-env/bin/activate  # Linux/macOS
   # or on Windows: iot-env\Scripts\activate
   
   # Verify activation (you should see (iot-env) in prompt)
   which python  # Should point to iot-env/bin/python
   ```

3. **Install Dependencies**
   ```bash
   # Install required Python packages
   pip install -r requirements.txt
   
   # Verify installation
   pip list  # Should show all installed packages
   ```

### Step 3: Verify File Structure

Ensure your project directory contains:
```
webapp/
├── enhanced_server.py          # Main application server
├── requirements.txt            # Python dependencies
├── sensor_data.csv            # Data storage (created automatically)
├── sensor_data.db             # SQLite database (created automatically)
├── templates/                 # Web interface templates
│   ├── base.html
│   ├── dashboard.html
│   ├── visualizations.html
│   ├── analytics.html
│   └── data_export.html
├── static/                    # CSS, JS, and generated charts
├── uploads/                   # File upload directory
├── exports/                   # Data export directory
└── iot-env/                   # Python virtual environment
```

---

## ⚙️ Configuration

### Step 1: Application Configuration

The application includes sensible defaults, but you can customize:

1. **Open enhanced_server.py**
   ```bash
   nano enhanced_server.py  # or use your preferred editor
   ```

2. **Key Configuration Variables** (lines 35-41):
   ```python
   CSV_FILE = 'sensor_data.csv'        # CSV data storage
   DB_FILE = 'sensor_data.db'          # SQLite database
   UPLOAD_FOLDER = 'uploads'           # File uploads
   EXPORT_FOLDER = 'exports'           # Data exports
   ```

3. **Flask Configuration** (line 33):
   ```python
   app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change for production
   ```

### Step 2: Network Configuration

1. **Find Raspberry Pi IP Address**
   ```bash
   # Method 1: Using hostname
   hostname -I
   
   # Method 2: Using ifconfig
   ifconfig wlan0 | grep inet
   
   # Method 3: Using ip command
   ip addr show wlan0
   ```

2. **Note Your IP Address** - You'll need this for smartphone configuration
   - Example: `192.168.1.100`

### Step 3: Firewall Configuration (if applicable)

```bash
# If using UFW firewall
sudo ufw allow 5000/tcp
sudo ufw reload

# For iptables (advanced users)
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

---

## 🚀 Running the Application

### Step 1: Start the Server

1. **Activate Virtual Environment** (if not already active)
   ```bash
   source iot-env/bin/activate
   ```

2. **Run the Application**
   ```bash
   python3 enhanced_server.py
   ```

3. **Expected Output**
   ```
   📊 IoT Sensor Data Collection & Visualization Server
   ✅ CSV file initialized: sensor_data.csv
   ✅ Database initialized: sensor_data.db
   ✅ Static directories created
   🌐 Server starting on: http://192.168.1.100:5000
   📱 Smartphone API endpoint: http://192.168.1.100:5000/api/sensor_data
   🖥️  Local access: http://localhost:5000
   * Running on all addresses (0.0.0.0)
   * Running on http://127.0.0.1:5000
   * Running on http://192.168.1.100:5000
   ```

### Step 2: Verify Server is Running

1. **Test Local Access**
   ```bash
   curl http://localhost:5000/api/stats
   ```

2. **Test Network Access**
   ```bash
   curl http://[YOUR_PI_IP]:5000/api/stats
   ```

### Step 3: Access Web Interface

Open a web browser and navigate to:
- **Local access**: `http://localhost:5000`
- **Network access**: `http://[YOUR_PI_IP]:5000`

You should see the dashboard with "No data available" until sensors start sending data.

---

## 📱 Smartphone Setup

### Option 1: Using Sensor Kinetics App (Recommended)

1. **Install App**
   - **iOS**: Download "Sensor Kinetics" from App Store
   - **Android**: Download "Sensor Kinetics" from Google Play Store

2. **Configure Data Streaming**
   - Open Sensor Kinetics
   - Go to Settings → Data Export
   - Enable "HTTP POST"
   - Set URL: `http://[YOUR_PI_IP]:5000/api/sensor_data`
   - Set interval: 1-5 seconds
   - Enable sensors: Accelerometer, Gyroscope, GPS

3. **Start Data Collection**
   - Return to main screen
   - Tap "Start Recording"
   - Data should appear in web interface within seconds

### Option 2: Using HTTP Request Apps

1. **Install HTTP Client**
   - **iOS**: "HTTP Client" or "Shortcuts" app
   - **Android**: "HTTP Request Shortcuts" or "Tasker"

2. **Create POST Request**
   ```json
   URL: http://[YOUR_PI_IP]:5000/api/sensor_data
   Method: POST
   Headers: Content-Type: application/json
   Body: {
     "timestamp": "2024-01-15T10:30:00Z",
     "device_id": "smartphone_01",
     "accelerometer": {"x": 0.5, "y": 0.2, "z": 9.8},
     "gyroscope": {"x": 0.1, "y": 0.05, "z": 0.02},
     "gps": {"latitude": 44.1569, "longitude": -77.1589, "altitude": 100, "speed": 0}
   }
   ```

### Option 3: Test with Sample Data

For testing without a smartphone app:
```bash
# Send test data using curl
curl -X POST http://localhost:5000/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-15T10:30:00Z",
    "device_id": "test_device",
    "accelerometer": {"x": 0.5, "y": 0.2, "z": 9.8},
    "gyroscope": {"x": 0.1, "y": 0.05, "z": 0.02},
    "gps": {"latitude": 44.1569, "longitude": -77.1589, "altitude": 100, "speed": 0}
  }'
```

---

## 🌐 Network Setup

### Step 1: Ensure Same Wi-Fi Network

1. **Raspberry Pi Wi-Fi Connection**
   ```bash
   # Check current connection
   iwconfig wlan0
   
   # Connect to Wi-Fi (if not connected)
   sudo raspi-config  # Select Network Options → Wi-Fi
   ```

2. **Verify Smartphone on Same Network**
   - Check smartphone Wi-Fi settings
   - Ensure connected to same network as Raspberry Pi

### Step 2: Test Network Connectivity

1. **From Smartphone to Pi**
   - Open web browser on smartphone
   - Navigate to `http://[PI_IP]:5000`
   - Should see web interface

2. **From Pi to Network**
   ```bash
   # Test internet connectivity
   ping google.com
   
   # Test local network
   ping [ROUTER_IP]
   ```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Server Won't Start

**Error**: `Permission denied` or `Port already in use`

**Solutions**:
```bash
# Check if port 5000 is in use
sudo netstat -tulpn | grep :5000

# Kill existing process
sudo kill -9 [PID]

# Try different port
python3 enhanced_server.py --port 8000
```

#### 2. Cannot Access from Smartphone

**Error**: `Connection refused` or `Timeout`

**Solutions**:
```bash
# Check Pi IP address
hostname -I

# Verify server is running
curl http://localhost:5000/api/stats

# Check firewall
sudo ufw status

# Test network connectivity
ping [SMARTPHONE_IP]  # From Pi
```

#### 3. No Data Appearing

**Error**: Data sent but not showing in interface

**Solutions**:
```bash
# Check server logs for errors
# Look at terminal output where server is running

# Test API directly
curl -X POST http://localhost:5000/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2024-01-15T10:30:00Z","device_id":"test"}'

# Check database
sqlite3 sensor_data.db "SELECT COUNT(*) FROM sensor_data;"
```

#### 4. Python Package Issues

**Error**: `ModuleNotFoundError` or import errors

**Solutions**:
```bash
# Activate virtual environment
source iot-env/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

---

## 📖 Usage Instructions

### Dashboard Features

1. **Real-time Monitoring**
   - Current sensor readings
   - Device connection status
   - Activity classification
   - System statistics

2. **Navigation**
   - Dashboard: Overview and real-time data
   - Visualizations: Interactive charts
   - Analytics: Historical analysis
   - Data Export: Download options

### Data Collection

1. **Start Collection**
   - Configure smartphone app
   - Begin data streaming
   - Monitor dashboard for incoming data

2. **Activity Types**
   - Stationary: Minimal movement
   - Walking: Moderate accelerometer activity
   - Running: High accelerometer activity
   - Unknown: Unclassified movement patterns

### Visualization Features

1. **Real-time Charts**
   - Live accelerometer data
   - Gyroscope readings
   - GPS tracking
   - Auto-refresh every 5 seconds

2. **3D Motion Plots**
   - Three-dimensional movement visualization
   - Interactive rotation and zoom
   - Time-based animation

3. **Activity Analysis**
   - Activity distribution pie charts
   - Movement pattern histograms
   - Speed analysis over time

---

## 🗂️ Data Management

### Database Structure

The SQLite database contains:
```sql
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    device_id TEXT NOT NULL,
    accel_x REAL, accel_y REAL, accel_z REAL,
    gyro_x REAL, gyro_y REAL, gyro_z REAL,
    latitude REAL, longitude REAL,
    altitude REAL, speed REAL,
    activity TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Data Export Options

1. **CSV Export**
   - Full dataset or date ranges
   - Customizable columns
   - Compatible with Excel/Google Sheets

2. **JSON Export**
   - Structured data format
   - API-compatible
   - Machine-readable

3. **Chart Images**
   - PNG format downloads
   - High-resolution graphics
   - Perfect for reports

---

## 🔌 API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main dashboard |
| GET | `/visualizations` | Interactive charts |
| GET | `/analytics` | Data analysis |
| GET | `/data-export` | Export interface |
| POST | `/api/sensor_data` | Submit sensor data |
| GET | `/api/stats` | System statistics |
| GET | `/api/data` | Retrieve sensor data |

### Sensor Data Submission

**Endpoint**: `POST /api/sensor_data`

**Request Format**:
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "device_id": "smartphone_01",
  "accelerometer": {
    "x": 0.5,
    "y": 0.2,
    "z": 9.8
  },
  "gyroscope": {
    "x": 0.1,
    "y": 0.05,
    "z": 0.02
  },
  "gps": {
    "latitude": 44.1569,
    "longitude": -77.1589,
    "altitude": 100.5,
    "speed": 0.0
  }
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Data stored successfully",
  "activity": "stationary",
  "record_id": 123
}
```

---

## 🎯 Quick Start Checklist

### Before Starting
- [ ] Raspberry Pi set up with Python 3.8+
- [ ] Project files downloaded to Pi
- [ ] Smartphone on same Wi-Fi network
- [ ] Monitor connected to Pi (for demo)

### Setup Steps
- [ ] Create virtual environment: `python3 -m venv iot-env`
- [ ] Activate environment: `source iot-env/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Find Pi IP address: `hostname -I`
- [ ] Start server: `python3 enhanced_server.py`

### Testing
- [ ] Access web interface at `http://[PI_IP]:5000`
- [ ] Configure smartphone app with API endpoint
- [ ] Send test data and verify it appears
- [ ] Navigate through all web interface sections

### Demo Ready
- [ ] Real-time data flowing
- [ ] All visualizations working
- [ ] Export functions tested
- [ ] Multiple devices can access interface

---

## 📞 Support Resources

### Key Files
- `README.md` - Project overview and features
- `GRADING_CHECKLIST.md` - Academic requirements
- `DEMO_GUIDE.md` - Demonstration instructions
- `requirements.txt` - Python dependencies

### Useful Commands
```bash
# Quick server start
cd webapp && source iot-env/bin/activate && python3 enhanced_server.py

# Check data
sqlite3 sensor_data.db "SELECT COUNT(*) FROM sensor_data;"

# Test API
curl http://localhost:5000/api/stats

# View IP address
hostname -I
```

---

**Your IoT sensor data collection system is now ready for use!**

Access the web interface and start collecting sensor data from your smartphone. For demonstrations, ensure both devices are on the same network and the server is running before beginning data collection. 