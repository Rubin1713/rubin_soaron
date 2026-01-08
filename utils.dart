import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:process_run/shell_run.dart';

class DateAndTimeManager extends DateTime {
  DateAndTimeManager.now() : super.now();

  static List<String> months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
  ];

  static List<String> days = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday'
  ];

  String getMonthName() {
    return months[month - 1];
  }

  String getMonthInitial() {
    return months[month - 1].substring(0, 3);
  }

  String getDayName() {
    return days[weekday - 1];
  }

  String getDayInitial() {
    return days[weekday - 1].substring(0, 3);
  }

  String getTimeFormat24() {
    return DateFormat('HH:mm').format(DateTime.now()).toString();
  }
}

// CUSTOM ICONS
class CustomIcons {
  CustomIcons._();

  static const _kFontFam = 'CustomIcons';
  static const String? _kFontPkg = null;

  static const IconData connect =
      IconData(0xe800, fontFamily: _kFontFam, fontPackage: _kFontPkg);
}

// CUSTOM COLOR
class CustomColors {
  static Color primary = Colors.cyan;
  static Color secondary = const Color.fromRGBO(60, 64, 72, 1);
}

class Utility {
  static Future<void> runPythonScript(fileName) async {
    try {
      // Path to your Python virtual environment activate script
      var venvActivatePath = './rc_connection/rc-env/bin/activate';
      // Path to your Python script
      var scriptPath = './rc_connection/$fileName';
      var sudoPassword = '9436';

      // Create a shell instance
      var shell = Shell();

      // Command to activate the virtual environment and run the script with sudo
      var command =
          'sh -c "cd \$PROJECT_PATH . $venvActivatePath && echo $sudoPassword | sudo -S python3 $scriptPath"';

      // Run the command
      await shell.run(command);
    } catch (e) {
      print('Error: $e');
    }
  }
/*
  static Future<void> killPorts() async {
    //await runPythonScript('close.py');
  }

 static void startWebsocket() {
  //runPythonScript('app.py');
  }
*/
static void startWebsocket() {
  // DISABLED — Python started manually
}

static Future<void> killPorts() async {
  // DISABLED
}

  static startCamera() {
    runPythonScript('camera.py');
  }
 
}
