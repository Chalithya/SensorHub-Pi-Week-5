#!/usr/bin/env node

/**
 * Local Test Server for IoT Sensor Data Collection
 * A simple Node.js server to test the React Native app locally
 * 
 * Usage:
 * 1. Install dependencies: npm install express cors
 * 2. Run server: node local_test_server.js
 * 3. Use your local IP address in the app (e.g., 192.168.1.XXX)
 * 
 * To find your local IP:
 * - Windows: ipconfig
 * - Mac/Linux: ifconfig or ip addr show
 */

const express = require('express');
const cors = require('cors');
const app = express();
const port = 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Store recent sensor data in memory
let sensorDataHistory = [];
const MAX_HISTORY = 100;

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    message: 'IoT Test Server is running!'
  });
});

// Main sensor data endpoint
app.post('/sensor_data', (req, res) => {
  const sensorData = req.body;
  
  console.log('\n📱 Received sensor data:', {
    timestamp: sensorData.timestamp,
    deviceId: sensorData.deviceId,
    accelerometer: sensorData.accelerometer,
    gyroscope: sensorData.gyroscope,
    location: sensorData.location
  });
  
  // Add to history
  sensorDataHistory.unshift({
    ...sensorData,
    receivedAt: new Date().toISOString()
  });
  
  // Keep only recent data
  if (sensorDataHistory.length > MAX_HISTORY) {
    sensorDataHistory = sensorDataHistory.slice(0, MAX_HISTORY);
  }
  
  // Send success response
  res.json({ 
    status: 'success',
    message: 'Sensor data received',
    timestamp: new Date().toISOString(),
    dataCount: sensorDataHistory.length
  });
});

// Get recent sensor data
app.get('/recent_data', (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  res.json({
    data: sensorDataHistory.slice(0, limit),
    total: sensorDataHistory.length
  });
});

// Statistics endpoint
app.get('/stats', (req, res) => {
  if (sensorDataHistory.length === 0) {
    return res.json({ message: 'No data received yet' });
  }
  
  const latestData = sensorDataHistory[0];
  const dataCount = sensorDataHistory.length;
  
  res.json({
    totalDataPoints: dataCount,
    latestTimestamp: latestData.timestamp,
    latestDevice: latestData.deviceId,
    latestLocation: latestData.location,
    serverUptime: process.uptime(),
    message: `Received ${dataCount} data points`
  });
});

// Start server
app.listen(port, '0.0.0.0', () => {
  console.log('\n🚀 IoT Test Server Started!');
  console.log(`📡 Server running on port ${port}`);
  console.log('\n📱 To use with the React Native app:');
  console.log('1. Find your computer\'s IP address:');
  console.log('   - Windows: Run "ipconfig" in cmd');
  console.log('   - Mac: Run "ifconfig" in terminal');
  console.log('   - Look for your local network IP (usually 192.168.x.x)');
  console.log('\n2. Enter that IP address in the app');
  console.log('3. Start data collection');
  console.log('\n🔍 Available endpoints:');
  console.log(`   - POST http://YOUR_IP:${port}/sensor_data (main endpoint)`);
  console.log(`   - GET  http://YOUR_IP:${port}/health (health check)`);
  console.log(`   - GET  http://YOUR_IP:${port}/recent_data (view recent data)`);
  console.log(`   - GET  http://YOUR_IP:${port}/stats (statistics)`);
  console.log('\n✅ Ready to receive sensor data!');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down server...');
  process.exit(0);
}); 