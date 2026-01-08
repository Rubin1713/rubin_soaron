
// NEW CODE ... FOR OLD CODE SEE BACKUP FOLDER

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService extends ChangeNotifier {
  WebSocketChannel? _channel;

  bool _isConnected = false;
  bool _hasData = false;

  // =========================
  // TELEMETRY FIELDS (PUBLIC)
  // =========================
  String batteryStatus = '';
  String armStatus = '';
  String flightMode = '';
  String longitude = '';
  String latitude = '';
  String altitude = '';
  String gpsFixType = '';
  String gpsStrength = '';
  String gpsSatellitesVisible = '';
  String speedVx = '';
  String speedVy = '';
  String speedVz = '';
  String groundSpeed = '';
  String heading = '';
  String roll = '';
  String pitch = '';
  String yaw = '';
  String lidarDistance = '';


  // =========================
  // STATE GETTERS
  // =========================
  bool get isConnected => _isConnected;			// INITIALISE TO false
  bool get hasData => _hasData;

  // =========================
  // CONNECT (CALL ONCE)
  // =========================
  void connect() {
    if (_channel != null) return;			// Websocket client connect here and server is present in app.py 

    debugPrint("🔌 Connecting to ws://127.0.0.1:8765");    

    _channel = WebSocketChannel.connect(		// connect to websocket server with default address
      Uri.parse("ws://127.0.0.1:8765"),
    );

    _channel!.stream.listen(				// listen to channel stream when server send data
      _onMessage,
      onDone: _onDisconnected,
      onError: _onError,
    );
  }

  // =========================
  // MESSAGE HANDLER
  // =========================
  void _onMessage(dynamic data) {
    debugPrint("📡 RAW TELEMETRY: $data");

    try {
      final decoded = jsonDecode(data);

      // EXPECTED FORMAT:
      // { "error": false, "message": { ...telemetry... } }
      if (decoded["error"] != false) return;

      final msg = decoded["message"];

      batteryStatus = msg["BATTERY_STATUS"].toString();
      armStatus = msg["ARM_STATUS"].toString();
      flightMode = msg["FLIGHT_MODE"].toString();
      longitude = msg["LONGITUDE"].toString();
      latitude = msg["LATITUDE"].toString();
      altitude = msg["ALTITUDE"].toString();
      gpsFixType = msg["GPS_FIX_TYPE"].toString();
      gpsStrength = msg["GPS_STRENGTH"].toString();
      gpsSatellitesVisible = msg["GPS_SATELLITES_VISIBLE"].toString();
      speedVx = msg["SPEED_VX"].toString();
      speedVy = msg["SPEED_VY"].toString();
      speedVz = msg["SPEED_VZ"].toString();
      groundSpeed = msg["GROUND_SPEED"].toString();
      heading = msg["HEADING"].toString();
      roll = msg["ROLL"].toString();
      pitch = msg["PITCH"].toString();
      yaw = msg["YAW"].toString();
      lidarDistance = msg["LIDAR_DISTANCE"]?.toString() ?? '';


      _isConnected = true;
      _hasData = true;

      notifyListeners();
    } catch (e) {
      debugPrint(" Telemetry parse error: $e");
    }
  }

  // =========================
  // DISCONNECT / ERROR
  // =========================
  void _onDisconnected() {
    debugPrint(" WebSocket disconnected");
    _isConnected = false;
    _hasData = false;
    _channel = null;
    notifyListeners();
  }

  void _onError(error) {
    debugPrint(" WebSocket error: $error");
    _onDisconnected();
  }

  @override
  void dispose() {                                        // closing channel 
    _channel?.sink.close();
    super.dispose();
  }
}

