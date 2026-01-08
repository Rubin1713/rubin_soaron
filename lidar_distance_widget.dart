import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:rc_app/services/websocket_service.dart';

class LidarDistanceWidget extends StatelessWidget {
  const LidarDistanceWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Selector<WebSocketService, String>(
      selector: (_, s) => s.lidarDistance,
      builder: (_, distance, __) {
        final value = double.tryParse(distance) ?? 0.0;

        Color color;
        if (value < 1.0) {
          color = Colors.red;
        } else if (value < 2.0) {
          color = Colors.orange;
        } else {
          color = Colors.green;
        }

        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.6),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: color, width: 2),
          ),
          child: Column(
            children: [
              const Text(
                'LiDAR Distance',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 26,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                '${value.toStringAsFixed(2)} m',
                style: TextStyle(
                  color: color,
                  fontSize: 42,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 5),
              Text(
                value < 1.0
                    ? '⚠ Obstacle Very Close'
                    : value < 2.0
                        ? '⚠ Obstacle Ahead'
                        : 'Clear',
                style: TextStyle(
                  color: color,
                  fontSize: 18,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

