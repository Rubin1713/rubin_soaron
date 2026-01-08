
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:provider/provider.dart';

import 'package:rc_app/constants/constants.dart';
import 'package:rc_app/layouts/home_layout.dart';
import 'package:rc_app/layouts/main_layout.dart';
import 'package:rc_app/services/drone_service.dart';
import 'package:rc_app/services/websocket_service.dart';
import 'package:rc_app/widgets/attitude_dial.dart';
import 'package:rc_app/widgets/button.dart';
import 'package:rc_app/widgets/compass.dart';
import 'package:rc_app/widgets/lidar_distance_widget.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {

  @override
void initState() {
  super.initState();
  WidgetsBinding.instance.addPostFrameCallback((_) {
   context.read<WebSocketService>().connect();
  });
}


  @override
  Widget build(BuildContext context) {
    return MainLayout(
      showControlBar: true,
      child: HomeLayout(
        showVideoStream: true,

        // =========================
        // TOP LEFT : TELEMETRY
        // =========================
        topLeft: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.5),
            borderRadius: BorderRadius.circular(4),
            border: Border.all(
              color: ConstantColors.primary,
              width: 2,
            ),
          ),
          child: Selector<WebSocketService, bool>(
            selector: (_, service) => service.isConnected,
            builder: (_, isConnected, __) {
              if (!isConnected) {
                return Text(
                  'Receiver is not connected',
                  style: Theme.of(context).textTheme.bodySmall,
                );
              }

 return SingleChildScrollView(
  child: Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    mainAxisSize: MainAxisSize.min,
    children: [

      /// SPEED XYZ
      Row(
        children: [
          _speedItem('X', (s) => s.speedVx),
          _speedItem('Y', (s) => s.speedVy),
          _speedItem('Z', (s) => s.speedVz),
        ],
      ),

      const SizedBox(height: 16),

      /// GPS DATA
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _textItem('Longitude', (s) => s.longitude),
          _textItem('Latitude', (s) => s.latitude),
          _textItem('GPS Fix', (s) => s.gpsFixType),
          _textItem('Satellites', (s) => s.gpsSatellitesVisible),
        ],
      ),

      const SizedBox(height: 16),

      /// LIDAR WIDGET
      const LidarDistanceWidget(),
    ],
  ),
);

            },
          ),
        ),

        // =========================
        // TOP CENTER : FLIGHT MODE
        // =========================
        topCenter: Selector<WebSocketService, String>(
          selector: (_, s) => s.flightMode,
          builder: (_, flightMode, __) {
            return Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SvgPicture.asset(
                  'assets/icons/in-flight.svg',
                  height: 25,
                ),
                const SizedBox(width: 10),
                Text(
                  flightMode,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            );
          },
        ),

        // =========================
        // TOP RIGHT : ATTITUDE
        // =========================
        topRight: const Row(
          children: [
            Compass(),
            SizedBox(width: 40),
            AttitudeDial(),
          ],
        ),

        // =========================
        // CENTER : STATUS
        // =========================
        center: DroneService.isScanning
            ? Column(
                children: [
                  SvgPicture.asset(
                    'assets/icons/arming.svg',
                    height: 50,
                  ),
                  Text(
                    'Scanning',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              )
            : DroneService.isScanningComplete
                ? Text(
                    'Scanning Completed',
                    style: Theme.of(context)
                        .textTheme
                        .bodySmall
                        ?.copyWith(color: Colors.green),
                  )
                : const SizedBox(),

        // =========================
        // BOTTOM CONTROLS
        // =========================
        bottomLeft: Button(
          text: 'Set Home',
          icon: SvgPicture.asset('assets/icons/home.svg', height: 40),
          onPressed: () => DroneService().setHomePosition(),
        ),

        bottomCenter: Button(
          text: DroneService.isArmed ? 'Disarm' : 'ARM',
          icon: SvgPicture.asset('assets/icons/arm.svg', height: 40),
          onPressed: () {
            DroneService.isArmed
                ? DroneService().disarm()
                : DroneService().arm();
            setState(() {});
          },
        ),

        bottomRight: Button(
          text: DroneService.isFlying ? 'Land' : 'Take Off',
          icon: SvgPicture.asset(
            DroneService.isFlying
                ? 'assets/icons/land.svg'
                : 'assets/icons/takeoff.svg',
            height: 40,
          ),
          onPressed: () {
            DroneService.isFlying
                ? DroneService().land()
                : DroneService().takeOff();
            setState(() {});
          },
        ),
      ),
    );
  }

  /// ---------------- HELPERS ----------------

Widget _speedItem(String title, String Function(WebSocketService) selector) {
  return Selector<WebSocketService, String>(
    selector: (_, s) => selector(s),
    builder: (_, value, __) {
      final speed = double.tryParse(value) ?? 0.0;

      return Row(
        children: [
          Text(
            title,
            style: const TextStyle(color: Colors.white, fontSize: 60),
          ),
          const SizedBox(width: 10),
          Text(
            speed.toStringAsFixed(2),
            style: const TextStyle(color: Colors.grey, fontSize: 40),
          ),
          const SizedBox(width: 10),
          const Text(
            'm/s',
            style: TextStyle(color: Colors.grey, fontSize: 30),
          ),
          const SizedBox(width: 20),
        ],
      );
    },
  );
}


  Widget _textItem(String title, String Function(WebSocketService) selector) {
    return Selector<WebSocketService, String>(
      selector: (_, s) => selector(s),
      builder: (_, value, __) {
        return Row(
          children: [
            Text('$title: ',
                style: const TextStyle(color: Colors.white, fontSize: 28)),
            Text(value,
                style: const TextStyle(color: Colors.grey, fontSize: 28)),
          ],
        );
      },
    );
  }
}

