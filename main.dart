/*import 'package:flutter/material.dart';
import 'package:get/route_manager.dart';
import 'package:provider/provider.dart';
import 'package:rc_app/constants/constants.dart';
import 'package:rc_app/screens/auth_screen.dart';
import 'package:rc_app/screens/home_screen.dart';
import 'package:rc_app/screens/init_screen.dart';
import 'package:rc_app/screens/model_screen.dart';
import 'package:rc_app/screens/paint_screen.dart';
import 'package:rc_app/screens/setup_screen.dart';
import 'package:rc_app/screens/welcome_screen.dart';
import 'package:rc_app/services/auth_service.dart';
import 'package:rc_app/services/battery_service.dart';
import 'package:rc_app/services/camera_service.dart';
import 'package:rc_app/services/http_service.dart';
import 'package:rc_app/services/storage_service.dart';
import 'package:rc_app/services/websocket_service.dart';
import 'package:rc_app/services/wifi_service.dart';
import 'package:rc_app/utils/utils.dart';
import 'package:window_manager/window_manager.dart';

void main() async {
  await StorageService.init();
  await Http.init();
  dynamic user = StorageService().read('user');
  if (user != null) {
    AuthService.isLoggedIn = true;
    AuthService.user = User.fromJson(StorageService().read('user'));
  } else {
    AuthService.isLoggedIn = false;
    AuthService.user = null;
  }
//  await Utility.killPorts();
 // Utility.startWebsocket();
  AuthService.isLoggedIn = true;
  AuthService.user = User(
  email: "dev@local",
  token: "dev-token",
);


  runApp(MultiProvider(
    providers: [
      ChangeNotifierProvider(
        create: (_) => CameraService(),
      ),
      ChangeNotifierProvider(
        create: (_) => WebSocketService(),
      ),
      ChangeNotifierProvider(
        create: (_) => BatteryService(),
      ),
      ChangeNotifierProvider(create: (_) => WifiService()),
    ],
    child: const MyApp(),
  ));
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> with WindowListener {
  @override
  void initState() {
    super.initState();
    Provider.of<BatteryService>(context, listen: false);
   // Provider.of<WebSocketService>(context, listen: false);
    Provider.of<WifiService>(context, listen: false);
    windowManager.setFullScreen(true);
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'Remote Control',
      // home: const SplashScreen(key: Key('splash')),
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Roboto',
        textTheme: TextTheme(
            labelLarge: TextStyle(
                color: Colors.white,
                fontFamily: 'Roboto',
                fontSize: TextSize.medium),
            labelMedium: const TextStyle(
                fontWeight: FontWeight.normal,
                color: Colors.white,
                fontFamily: 'Roboto',
                fontSize: 35),
            bodyLarge: const TextStyle(
                color: Colors.white,
                fontFamily: 'Roboto',
                fontWeight: FontWeight.normal,
                fontSize: 60),
            bodyMedium: const TextStyle(
                color: Colors.white,
                fontFamily: 'Roboto',
                fontWeight: FontWeight.normal,
                fontSize: 45),
            bodySmall: const TextStyle(
                color: Colors.white,
                fontFamily: 'Roboto',
                fontWeight: FontWeight.w200,
                fontSize: 30),
            titleLarge: const TextStyle(
                color: Colors.white,
                letterSpacing: 1.5,
                fontWeight: FontWeight.bold,
                fontSize: 100),
            titleMedium: const TextStyle(
                color: Colors.white,
                fontFamily: 'Roboto',
                letterSpacing: 1.5,
                fontSize: 60),
            titleSmall: const TextStyle(
                color: Colors.white, fontFamily: 'Roboto', fontSize: 25)),
      ),
      initialRoute: AuthService.isLoggedIn ? '/home' : '/welcome',
      routes: {
        // '/': (context) => const SplashScreen(key: Key('splash')),
        '/welcome': (context) => const WelcomeScreen(),
        '/auth': (context) => const AuthScreen(),
        '/setup': (context) => const SetupScreen(),
        '/home': (context) => const HomeScreen(),
        '/model': (context) => const ModelScreen(),
        '/init': (context) => const InitScreen(),
        '/paint': (context) => const PaintScreen(),
        // '/test': (context) => HtmlPage(),
      },
    );
  }
}
*/

// The above code is old cod

//------------------------------------------------------------------------------------------------------------

// New code

import 'package:flutter/material.dart';
import 'package:get/route_manager.dart';
import 'package:provider/provider.dart';
import 'package:rc_app/constants/constants.dart';
import 'package:rc_app/screens/auth_screen.dart';
import 'package:rc_app/screens/home_screen.dart';
import 'package:rc_app/screens/init_screen.dart';
import 'package:rc_app/screens/model_screen.dart';
import 'package:rc_app/screens/paint_screen.dart';
import 'package:rc_app/screens/setup_screen.dart';
import 'package:rc_app/screens/welcome_screen.dart';
import 'package:rc_app/services/auth_service.dart';
import 'package:rc_app/services/battery_service.dart';
import 'package:rc_app/services/camera_service.dart';
import 'package:rc_app/services/http_service.dart';
import 'package:rc_app/services/storage_service.dart';
import 'package:rc_app/services/websocket_service.dart';
import 'package:rc_app/services/wifi_service.dart';
import 'package:window_manager/window_manager.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await StorageService.init();
  await Http.init();

  // 🔹 DEV LOGIN (OK for now)
  AuthService.isLoggedIn = true;
  AuthService.user = User(
    email: "dev@local",
    token: "dev-token",
  );

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CameraService()),
        ChangeNotifierProvider(create: (_) => WebSocketService()),
        ChangeNotifierProvider(create: (_) => BatteryService()),
        ChangeNotifierProvider(create: (_) => WifiService()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> with WindowListener {
  @override
  void initState() {
    super.initState();

    // ✅ DO NOT TOUCH WebSocketService HERE
    Provider.of<BatteryService>(context, listen: false);
    Provider.of<WifiService>(context, listen: false);

    windowManager.setFullScreen(true);
  }

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'Remote Control',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Roboto',
        textTheme: TextTheme(
          labelLarge: TextStyle(
            color: Colors.white,
            fontSize: TextSize.medium,
          ),
          labelMedium: const TextStyle(
            color: Colors.white,
            fontSize: 35,
          ),
          bodyLarge: const TextStyle(
            color: Colors.white,
            fontSize: 60,
          ),
          bodyMedium: const TextStyle(
            color: Colors.white,
            fontSize: 45,
          ),
          bodySmall: const TextStyle(
            color: Colors.white,
            fontSize: 30,
          ),
          titleLarge: const TextStyle(
            color: Colors.white,
            fontSize: 100,
            fontWeight: FontWeight.bold,
          ),
          titleMedium: const TextStyle(
            color: Colors.white,
            fontSize: 60,
          ),
          titleSmall: const TextStyle(
            color: Colors.white,
            fontSize: 25,
          ),
        ),
      ),
      initialRoute: '/home',
      routes: {
        '/welcome': (_) => const WelcomeScreen(),
        '/auth': (_) => const AuthScreen(),
        '/setup': (_) => const SetupScreen(),
        '/home': (_) => const HomeScreen(),
        '/model': (_) => const ModelScreen(),
        '/init': (_) => const InitScreen(),
        '/paint': (_) => const PaintScreen(),
      },
    );
  }
}

