import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  SafeAreaView,
  Platform,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Accelerometer, Gyroscope } from 'expo-sensors';
import * as Location from 'expo-location';
import * as Device from 'expo-device';
import axios from 'axios';

interface SensorData {
  timestamp: string;
  device_id: string;
  accel_x: number;
  accel_y: number;
  accel_z: number;
  gyro_x: number;
  gyro_y: number;
  gyro_z: number;
  latitude: number;
  longitude: number;
  altitude: number;
  speed: number;
}

interface AccelerometerData {
  x: number;
  y: number;
  z: number;
}

interface GyroscopeData {
  x: number;
  y: number;
  z: number;
}

export default function App() {
  // State variables
  const [piIPAddress, setPiIPAddress] = useState('192.168.137.25');
  const [isCollecting, setIsCollecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connected' | 'error'>('disconnected');
  const [transmissionCount, setTransmissionCount] = useState(0);
  const [lastTransmissionTime, setLastTransmissionTime] = useState<string>('Never');
  const [currentActivity, setCurrentActivity] = useState<string>('stationary');
  
  // Sensor data states
  const [accelerometerData, setAccelerometerData] = useState<AccelerometerData>({ x: 0, y: 0, z: 0 });
  const [gyroscopeData, setGyroscopeData] = useState<GyroscopeData>({ x: 0, y: 0, z: 0 });
  const [locationData, setLocationData] = useState({ latitude: 0, longitude: 0, altitude: 0, speed: 0 });
  const [deviceId, setDeviceId] = useState<string>('');
  const [hasValidLocation, setHasValidLocation] = useState<boolean>(false);

  // Refs for subscriptions and intervals
  const accelerometerSubscription = useRef<any>(null);
  const gyroscopeSubscription = useRef<any>(null);
  const locationSubscription = useRef<any>(null);
  const transmissionInterval = useRef<any>(null);
  const monitoringInterval = useRef<any>(null);
  const sensorDataBuffer = useRef<SensorData[]>([]);
  const previousValues = useRef({ acc: {x:0,y:0,z:0}, gyro: {x:0,y:0,z:0}, gps: {lat:0,lng:0} });
  
  // Refs for latest sensor data (for immediate transmission)
  const latestAccelerometerData = useRef<AccelerometerData>({ x: 0, y: 0, z: 0 });
  const latestGyroscopeData = useRef<GyroscopeData>({ x: 0, y: 0, z: 0 });
  const latestLocationData = useRef({ latitude: 0, longitude: 0, altitude: 0, speed: 0 });

  // Initialize device ID and request permissions
  useEffect(() => {
    initializeApp();
    return () => {
      cleanup();
    };
  }, []);

  const initializeApp = async () => {
    console.log('🚀 Initializing IoT Sensor App...');
    
    // Get device ID
    const deviceName = Device.deviceName || 'Unknown';
    const brand = Device.brand || 'Unknown';
    const generatedDeviceId = `${brand}_${deviceName}_${Math.random().toString(36).substr(2, 9)}`;
    setDeviceId(generatedDeviceId);
    
    console.log('📱 Device Info:', {
      deviceName: deviceName,
      brand: brand,
      deviceId: generatedDeviceId,
      platform: Platform.OS
    });

    // Request location permissions
    console.log('🔐 Requesting location permissions...');
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Location permission is required for GPS tracking. Using default values.');
      console.log('❌ Location permission denied - will use default coordinates');
    } else {
      console.log('✅ Location permission granted');
      // Try to get initial location
      try {
        const currentLocation = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.High,
        });
        const initialLocation = {
          latitude: currentLocation.coords.latitude || 0,
          longitude: currentLocation.coords.longitude || 0,
          altitude: currentLocation.coords.altitude || 0,
          speed: currentLocation.coords.speed || 0,
        };
        setLocationData(initialLocation);
        setHasValidLocation(true);
        console.log(`gps[lat:${initialLocation.latitude.toFixed(6)}, lng:${initialLocation.longitude.toFixed(6)}, spd:${initialLocation.speed.toFixed(2)}, alt:${initialLocation.altitude.toFixed(2)}]`);
      } catch (error) {
        console.log('⚠️ Could not get initial location:', (error as Error).message);
      }
    }
    
    console.log('🎉 App initialization complete!');
  };

  const cleanup = () => {
    stopDataCollection();
  };

  const validateIPAddress = (input: string): boolean => {
    // Check if it's a full URL
    if (input.startsWith('http://') || input.startsWith('https://')) {
      try {
        new URL(input);
        return true;
      } catch {
        return false;
      }
    }
    
    // Check if it's just an IP address
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(input);
  };

  const determineActivity = (accel: AccelerometerData, gyro: GyroscopeData, speed: number | null): string => {
    const accelMagnitude = Math.sqrt(accel.x ** 2 + accel.y ** 2 + accel.z ** 2);
    const gyroMagnitude = Math.sqrt(gyro.x ** 2 + gyro.y ** 2 + gyro.z ** 2);
    
    if (speed && speed > 10) {
      return 'driving';
    } else if (speed && speed > 2) {
      return 'running';
    } else if (accelMagnitude > 10.5 || gyroMagnitude > 0.5) {
      return 'walking';
    } else {
      return 'stationary';
    }
  };

  const startSensorCollection = async () => {
    console.log('🚀 Starting sensor collection...');
    
    // Check if sensors are available
    const isAccelerometerAvailable = await Accelerometer.isAvailableAsync();
    const isGyroscopeAvailable = await Gyroscope.isAvailableAsync();
    
    console.log('📱 Sensor availability check:');
    console.log(`   Accelerometer: ${isAccelerometerAvailable ? '✅ Available' : '❌ Not Available'}`);
    console.log(`   Gyroscope: ${isGyroscopeAvailable ? '✅ Available' : '❌ Not Available'}`);
    
    if (!isAccelerometerAvailable) {
      console.log('⚠️ Warning: Accelerometer not available - using default values');
    }
    if (!isGyroscopeAvailable) {
      console.log('⚠️ Warning: Gyroscope not available - using default values');
    }
    
    // Set update intervals
    Accelerometer.setUpdateInterval(100); // 100ms
    Gyroscope.setUpdateInterval(100); // 100ms
    
    console.log('📱 Sensor update intervals set: Accelerometer & Gyroscope = 100ms');

    // Start accelerometer
    try {
      accelerometerSubscription.current = Accelerometer.addListener((data) => {
        const newData = {
          x: Number(data.x) || 0,
          y: Number(data.y) || 0,
          z: Number(data.z) || 0
        };
        setAccelerometerData(newData);
        latestAccelerometerData.current = newData; // Store in ref for immediate access
        console.log(`🔄 Accelerometer update: [${newData.x.toFixed(3)}, ${newData.y.toFixed(3)}, ${newData.z.toFixed(3)}]`);
      });
      console.log('✅ Accelerometer listener started successfully');
    } catch (error) {
      console.error('❌ Failed to start accelerometer:', error);
    }

    // Start gyroscope
    try {
      gyroscopeSubscription.current = Gyroscope.addListener((data) => {
        const newData = {
          x: Number(data.x) || 0,
          y: Number(data.y) || 0,
          z: Number(data.z) || 0
        };
        setGyroscopeData(newData);
        latestGyroscopeData.current = newData; // Store in ref for immediate access
        console.log(`🌀 Gyroscope update: [${newData.x.toFixed(3)}, ${newData.y.toFixed(3)}, ${newData.z.toFixed(3)}]`);
      });
      console.log('✅ Gyroscope listener started successfully');
    } catch (error) {
      console.error('❌ Failed to start gyroscope:', error);
    }

    console.log('✅ Accelerometer and Gyroscope listeners started');

    // Start location tracking
    try {
      console.log('🌍 Starting GPS location tracking...');
      locationSubscription.current = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 2000, // 2 seconds
          distanceInterval: 1,
        },
        (location) => {
          const locationInfo = {
            latitude: location.coords.latitude || 0,
            longitude: location.coords.longitude || 0,
            altitude: location.coords.altitude || 0,
            speed: location.coords.speed || 0,
          };
          setLocationData(locationInfo);
          latestLocationData.current = locationInfo; // Store in ref for immediate access
          setHasValidLocation(true);
          console.log(`📍 GPS update: [${locationInfo.latitude.toFixed(6)}, ${locationInfo.longitude.toFixed(6)}, alt:${locationInfo.altitude.toFixed(2)}, spd:${locationInfo.speed.toFixed(2)}]`);
        }
      );
      console.log('✅ GPS location tracking started');
    } catch (error) {
      console.error('❌ Error starting location tracking:', error);
    }
  };

  const stopSensorCollection = () => {
    console.log('🛑 Stopping sensor collection...');
    
    if (accelerometerSubscription.current) {
      accelerometerSubscription.current.remove();
      accelerometerSubscription.current = null;
      console.log('📊 Accelerometer listener stopped');
    }
    if (gyroscopeSubscription.current) {
      gyroscopeSubscription.current.remove();
      gyroscopeSubscription.current = null;
      console.log('🌀 Gyroscope listener stopped');
    }
    if (locationSubscription.current && locationSubscription.current.remove) {
      locationSubscription.current.remove();
      locationSubscription.current = null;
      console.log('📍 GPS location tracking stopped');
    }
    
    console.log('✅ All sensors stopped successfully');
  };

  const startDataTransmission = () => {
    console.log('🔄 Starting data transmission to Pi (every 1.5 seconds)...');
    
    // Start monitoring for value changes
    monitoringInterval.current = setInterval(() => {
      const accChanged = Math.abs(accelerometerData.x - previousValues.current.acc.x) > 0.001 ||
                        Math.abs(accelerometerData.y - previousValues.current.acc.y) > 0.001 ||
                        Math.abs(accelerometerData.z - previousValues.current.acc.z) > 0.001;
      const gyroChanged = Math.abs(gyroscopeData.x - previousValues.current.gyro.x) > 0.001 ||
                         Math.abs(gyroscopeData.y - previousValues.current.gyro.y) > 0.001 ||
                         Math.abs(gyroscopeData.z - previousValues.current.gyro.z) > 0.001;
      const gpsChanged = Math.abs(locationData.latitude - previousValues.current.gps.lat) > 0.000001 ||
                        Math.abs(locationData.longitude - previousValues.current.gps.lng) > 0.000001;
      
      // Update previous values
      previousValues.current = {
        acc: { x: accelerometerData.x, y: accelerometerData.y, z: accelerometerData.z },
        gyro: { x: gyroscopeData.x, y: gyroscopeData.y, z: gyroscopeData.z },
        gps: { lat: locationData.latitude, lng: locationData.longitude }
      };
    }, 10000); // Monitor every 10 seconds
    
    let transmissionCounter = 0;
    
    transmissionInterval.current = setInterval(() => {
      transmissionCounter++;
      
      // Use ref data for immediate access to latest sensor values
      const currentAccel = latestAccelerometerData.current;
      const currentGyro = latestGyroscopeData.current;
      const currentLocation = latestLocationData.current;
      
      // Always create fresh sensor reading with current values from refs
      const currentReading: SensorData = {
        timestamp: new Date().toISOString(),
        device_id: deviceId,
        accel_x: Number(currentAccel.x) || 0,
        accel_y: Number(currentAccel.y) || 0,
        accel_z: Number(currentAccel.z) || 0,
        gyro_x: Number(currentGyro.x) || 0,
        gyro_y: Number(currentGyro.y) || 0,
        gyro_z: Number(currentGyro.z) || 0,
        latitude: Number(currentLocation.latitude) || 0,
        longitude: Number(currentLocation.longitude) || 0,
        altitude: Number(currentLocation.altitude) || 0,
        speed: Number(currentLocation.speed) || 0
      };
      
      // Update activity based on current data
      const activity = determineActivity(currentAccel, currentGyro, currentLocation.speed);
      setCurrentActivity(activity);
      
      console.log(`tx[${transmissionCounter}] acc[${currentReading.accel_x.toFixed(3)},${currentReading.accel_y.toFixed(3)},${currentReading.accel_z.toFixed(3)}] | gyro[${currentReading.gyro_x.toFixed(3)},${currentReading.gyro_y.toFixed(3)},${currentReading.gyro_z.toFixed(3)}] | gps[${currentReading.latitude.toFixed(6)},${currentReading.longitude.toFixed(6)}] | activity: ${activity}`);
      
      sensorDataBuffer.current = [currentReading];
      sendDataToPi(transmissionCounter);
    }, 1500); // Send every 1.5 seconds
    
    console.log('✅ Data transmission timer started');
  };

  const stopDataTransmission = () => {
    console.log('🔄 Stopping data transmission...');
    
    if (transmissionInterval.current) {
      clearInterval(transmissionInterval.current);
      transmissionInterval.current = null;
      console.log('✅ Data transmission timer stopped');
    }
    
    if (monitoringInterval.current) {
      clearInterval(monitoringInterval.current);
      monitoringInterval.current = null;
    }
  };

  const sendDataToPi = async (txCount?: number) => {
    if (!validateIPAddress(piIPAddress)) {
      setConnectionStatus('error');
      Alert.alert('Invalid Address', 'Please enter a valid IP address or URL');
      console.log('❌ Invalid IP address/URL:', piIPAddress);
      return;
    }

    // Build the URL - if it's already a full URL, use it; if it's just an IP, add http and port
    let url: string;
    if (piIPAddress.startsWith('http://') || piIPAddress.startsWith('https://')) {
      // If it's already a full URL, append the endpoint
      url = piIPAddress.endsWith('/') ? `${piIPAddress}api/sensor_data` : `${piIPAddress}/api/sensor_data`;
    } else {
      // If it's just an IP address, add the protocol and port
      url = `http://${piIPAddress}:5000/api/sensor_data`;
    }

    try {
      const dataToSend = sensorDataBuffer.current[0]; // Send latest reading
      
      console.log(`sending -> ${url.split('//')[1]?.split('/')[0] || 'unknown'} | data ready`);
      
      const response = await axios.post(url, dataToSend, {
        timeout: 5000,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 200) {
        setConnectionStatus('connected');
        setTransmissionCount(prev => prev + 1);
        setLastTransmissionTime(new Date().toLocaleTimeString());
        sensorDataBuffer.current = [];
        
        console.log(`sent ✓ | tx[${txCount || 'unknown'}] | ${new Date().toLocaleTimeString()}`);
      }
    } catch (error) {
      setConnectionStatus('error');
      console.error('❌ Error sending data to Pi:', {
        error: (error as Error).message,
        code: (error as any).code,
        url: url,
        timestamp: new Date().toLocaleTimeString()
      });
    }
  };

  const startDataCollection = async () => {
    console.log('🎯 START DATA COLLECTION INITIATED');
    console.log('📱 Target Address:', piIPAddress);
    
    if (!validateIPAddress(piIPAddress)) {
      Alert.alert('Invalid Address', 'Please enter a valid IP address or URL');
      console.log('❌ Data collection failed - Invalid address');
      return;
    }
    
    console.log('✅ Address validated');
    console.log('🚀 Starting IoT sensor data collection...');
    
    setIsCollecting(true);
    setTransmissionCount(0);
    
    console.log('📊 Device ID:', deviceId);
    
    // Build destination URL for logging
    let destinationUrl: string;
    if (piIPAddress.startsWith('http://') || piIPAddress.startsWith('https://')) {
      destinationUrl = piIPAddress.endsWith('/') ? `${piIPAddress}api/sensor_data` : `${piIPAddress}/api/sensor_data`;
    } else {
      destinationUrl = `http://${piIPAddress}:5000/api/sensor_data`;
    }
    console.log('🎯 Destination:', destinationUrl);
    
    await startSensorCollection();
    startDataTransmission();
    
    console.log('🎉 DATA COLLECTION STARTED SUCCESSFULLY!');
    console.log('=' .repeat(50));
  };

  const stopDataCollection = () => {
    console.log('🛑 STOP DATA COLLECTION INITIATED');
    
    setIsCollecting(false);
    setConnectionStatus('disconnected');
    stopSensorCollection();
    stopDataTransmission();
    sensorDataBuffer.current = [];
    
    console.log('🎉 DATA COLLECTION STOPPED SUCCESSFULLY!');
    console.log('📊 Final transmission count:', transmissionCount);
    console.log('=' .repeat(50));
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#4CAF50';
      case 'error': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const formatNumber = (num: number): string => {
    return num.toFixed(3);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="auto" />
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>IoT Sensor Data Collector</Text>
          <View style={styles.statusContainer}>
            <View style={[styles.statusDot, { backgroundColor: getConnectionStatusColor() }]} />
            <Text style={styles.statusText}>
              {connectionStatus === 'connected' ? 'Connected' : 
               connectionStatus === 'error' ? 'Error' : 'Disconnected'}
            </Text>
          </View>
        </View>

        {/* Server Address Input */}
        <View style={styles.inputContainer}>
          <Text style={styles.label}>Server Address:</Text>
          <TextInput
            style={styles.input}
            value={piIPAddress}
            onChangeText={setPiIPAddress}
            placeholder="192.168.1.100 or http://127.0.0.1:5000"
            keyboardType="default"
            autoCapitalize="none"
            autoCorrect={false}
            editable={!isCollecting}
          />
        </View>

        {/* Control Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, isCollecting ? styles.stopButton : styles.startButton]}
            onPress={isCollecting ? stopDataCollection : startDataCollection}
          >
            <Text style={styles.buttonText}>
              {isCollecting ? 'STOP COLLECTION' : 'START COLLECTION'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Transmissions:</Text>
            <Text style={styles.statValue}>{transmissionCount}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Last Sent:</Text>
            <Text style={styles.statValue}>{lastTransmissionTime}</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Activity:</Text>
            <Text style={[styles.statValue, styles.activityText]}>{currentActivity}</Text>
          </View>
        </View>

        {/* Sensor Data Display */}
        <View style={styles.sensorContainer}>
          <Text style={styles.sensorTitle}>Real-time Sensor Data</Text>
          
          {/* Accelerometer */}
          <View style={styles.sensorSection}>
            <Text style={styles.sensorLabel}>Accelerometer (m/s²):</Text>
            <View style={styles.sensorData}>
              <Text style={styles.sensorValue}>X: {formatNumber(accelerometerData.x)}</Text>
              <Text style={styles.sensorValue}>Y: {formatNumber(accelerometerData.y)}</Text>
              <Text style={styles.sensorValue}>Z: {formatNumber(accelerometerData.z)}</Text>
            </View>
          </View>

          {/* Gyroscope */}
          <View style={styles.sensorSection}>
            <Text style={styles.sensorLabel}>Gyroscope (rad/s):</Text>
            <View style={styles.sensorData}>
              <Text style={styles.sensorValue}>X: {formatNumber(gyroscopeData.x)}</Text>
              <Text style={styles.sensorValue}>Y: {formatNumber(gyroscopeData.y)}</Text>
              <Text style={styles.sensorValue}>Z: {formatNumber(gyroscopeData.z)}</Text>
            </View>
          </View>

          {/* Location */}
          <View style={styles.sensorSection}>
            <Text style={styles.sensorLabel}>GPS Location:</Text>
            <View style={styles.sensorData}>
              <Text style={styles.sensorValue}>Lat: {formatNumber(locationData.latitude)}</Text>
              <Text style={styles.sensorValue}>Lng: {formatNumber(locationData.longitude)}</Text>
              <Text style={styles.sensorValue}>
                Alt: {locationData.altitude ? formatNumber(locationData.altitude) : 'N/A'}m
              </Text>
              <Text style={styles.sensorValue}>
                Speed: {locationData.speed ? formatNumber(locationData.speed) : '0'} m/s
              </Text>
            </View>
          </View>

          {/* Device Info */}
          <View style={styles.sensorSection}>
            <Text style={styles.sensorLabel}>Device ID:</Text>
            <Text style={styles.deviceId}>{deviceId}</Text>
          </View>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {
    fontSize: 16,
    color: '#666',
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  buttonContainer: {
    marginBottom: 30,
  },
  button: {
    borderRadius: 25,
    padding: 20,
    alignItems: 'center',
    elevation: 3,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  startButton: {
    backgroundColor: '#4CAF50',
  },
  stopButton: {
    backgroundColor: '#F44336',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  statsContainer: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  statLabel: {
    fontSize: 16,
    color: '#666',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  activityText: {
    color: '#2196F3',
    textTransform: 'capitalize',
  },
  sensorContainer: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sensorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  sensorSection: {
    marginBottom: 20,
  },
  sensorLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#444',
    marginBottom: 8,
  },
  sensorData: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  sensorValue: {
    fontSize: 14,
    color: '#666',
    backgroundColor: '#f8f8f8',
    padding: 8,
    borderRadius: 8,
    marginBottom: 5,
    minWidth: '30%',
    textAlign: 'center',
  },
  deviceId: {
    fontSize: 12,
    color: '#888',
    backgroundColor: '#f8f8f8',
    padding: 10,
    borderRadius: 8,
    textAlign: 'center',
  },
});
