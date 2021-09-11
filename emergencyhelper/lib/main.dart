import 'dart:io';
import 'dart:async';
import 'dart:convert';
import 'dart:developer';

import 'package:device_info/device_info.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'package:location/location.dart';
import 'package:shared_preferences/shared_preferences.dart';

const double CAMERA_ZOOM = 16.5;
const LatLng SOURCE_LOCATION = LatLng(37.5427, 126.9664);

const AndroidNotificationChannel channel = AndroidNotificationChannel(
  'my_channel', // id
  'My Channel', // title
  'Important notifications from my server.', // description
  importance: Importance.high,
);

Future<Map<String, dynamic>> fetchAPI(type, serial, key, token) async {
  try {
    var response;
    if (type == "register") {
      response = await http.post(
          Uri.parse('http://61.73.71.185/api/' + type),
          headers: <String, String> {
            'Content-Type': 'application/json',
          },
          body: jsonEncode(<String, String>{
            'serial': serial,
            'key': key,
            'token': token
          }),
        );
    } else if (type == "login") {
      response = await http.post(
        Uri.parse('http://61.73.71.185/api/' + type),
        headers: <String, String> {
          'Content-Type': 'application/json',
        },
        body: jsonEncode(<String, String>{
          'serial': serial,
          'key': key
        }),
      );
    }
    return json.decode(response.body);
  } catch(e) {}
}

Future<Map<String, dynamic>> parseLocation() async {
  final prefs = await SharedPreferences.getInstance();
  try {
    final response =
    await http.get(
        Uri.parse('http://61.73.71.185/api/location'),
        headers: {
          'Authorization': 'Bearer ' + prefs.getString('token')
        });

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load API');
    }
  } catch(e) {}
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({Key key}) : super(key: key);

  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final Completer<GoogleMapController> _controller = Completer();
  final FirebaseMessaging messaging = FirebaseMessaging.instance;

  Set<Marker> _markers = Set<Marker>();

  LocationData currentLocation;
  LocationData destinationLocation;
  Location location;

  Timer _timer;
  @override
  void initState() {
    super.initState();
    
    initializeFlutterFire();
    saveFirebaseToken();
    firebaseCloudMessaging_Listeners();

    getLoginToken();

    location = new Location();

    setInitialLocation();

    _timer = Timer.periodic(const Duration(seconds: 3), (v) {
      setState(() {
        location.getLocation().then((value) => currentLocation);

        setDestinationLocation();
        updateCameraPosition();
      });
    });

  }

  @override
  void dispose() {
    super.dispose();

    if (_timer != null) {
      _timer.cancel();
      _timer = null;
    }
  }

  //파이어베이스 초기화 함수
  void initializeFlutterFire() async {
    try {
      // Wait for Firebase to initialize and set `_initialized` state to true
      await messaging
          .setForegroundNotificationPresentationOptions(
        alert: true,
        badge: true,
        sound: true,
      );
    } catch (e) {
      log(e);
    }
  }

  void firebaseCloudMessaging_Listeners() {
    final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();

    FirebaseMessaging.onBackgroundMessage((RemoteMessage message) {
      RemoteNotification notification = message.notification;

      if (notification != null) {
        flutterLocalNotificationsPlugin.show(
            notification.hashCode,
            notification.title,
            notification.body,
            NotificationDetails(
                android: AndroidNotificationDetails(
                  channel.id,
                  channel.name,
                  channel.description,
                  // icon: '',
                )
            )
        );
      }
    });
  }

  void saveFirebaseToken() async {
    String _token = await messaging.getToken();
    final prefs = await SharedPreferences.getInstance();
    prefs.setString('FirebaseToken', _token);
  }

  Future<String> loadFirebaseToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('FirebaseToken') ?? 'None';
  }

  void setInitialLocation() async {
    currentLocation = await location.getLocation();
    destinationLocation = LocationData.fromMap({
      "latitude": 37.5427,
      "longitude": 126.9664,
    });
  }

  @override
  Widget build(BuildContext context) {
    CameraPosition initialCameraPosition = CameraPosition(
        zoom: CAMERA_ZOOM,
        target: SOURCE_LOCATION);
    if (currentLocation != null) {
      initialCameraPosition = CameraPosition(
          target: LatLng(currentLocation.latitude, currentLocation.longitude),
          zoom: CAMERA_ZOOM);
    }
    return MaterialApp(
      title: 'Fetch Data Example',
      home: Scaffold(
        body: Stack(
          children: <Widget>[
            GoogleMap(
              myLocationEnabled: true,
              compassEnabled: true,
              markers: _markers,
              mapType: MapType.normal,
              initialCameraPosition: initialCameraPosition,
              onMapCreated: (GoogleMapController controller) {
                _controller.complete(controller);

                showPinsOnMap();
              },
            ),
          ],
        ),
      ),
    );
  }

  void showPinsOnMap() {
    var pinPosition = LatLng(currentLocation.latitude, currentLocation.longitude);
    var destPosition = LatLng(destinationLocation.latitude, destinationLocation.longitude);


    _markers.add(Marker(
      markerId: MarkerId('sourcePin'),
      position: pinPosition,
      // icon: sourceIcon
    ));
    // destination pin
    _markers.add(Marker(
      markerId: MarkerId('destPin'),
      position: destPosition,
      // icon: destinationIcon
    ));
    // set the route lines on the map from source to destination
    // for more info follow this tutorial
  }

  void setDestinationLocation() async {
    final decoded = await parseLocation();
    destinationLocation = LocationData.fromMap({
      "latitude": decoded['latitude'],
      "longitude": decoded['longitude'],
    });
  }

  void updateCameraPosition() async {
    CameraPosition cPosition = CameraPosition(
      zoom: CAMERA_ZOOM,
      target: LatLng(destinationLocation.latitude, destinationLocation.longitude),
    );
    final GoogleMapController controller = await _controller.future;
    // controller.animateCamera(CameraUpdate.newCameraPosition(cPosition));

    setState(() {
      var pinPosition = LatLng(currentLocation.latitude, currentLocation.longitude);
      var destPosition = LatLng(destinationLocation.latitude, destinationLocation.longitude);

      _markers.removeWhere((m) => m.markerId.value == 'sourcePin');
      _markers.removeWhere((m) => m.markerId.value == 'destPin');
      _markers.add(Marker(
        markerId: MarkerId('sourcePin'),
        position: pinPosition,
      ));
      // destination pin
      _markers.add(Marker(
        markerId: MarkerId('destPin'),
        position: destPosition,
      ));
    });
  }

  void getLoginToken() async {
    final prefs = await SharedPreferences.getInstance();
    var token = prefs.getString('token') ?? 'none';

    DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
    AndroidDeviceInfo androidInfo = await deviceInfo.androidInfo;

    var imei = androidInfo.androidId;
    String firebase = await loadFirebaseToken();
    log(token);
    var result;
    if (token == 'none') {
      await fetchAPI('register', imei, "0000000061c8eda7", firebase);
      result = await fetchAPI('login', imei, "0000000061c8eda7", firebase);
      if (result['status'] == 'Login Success!!') {
        prefs.setString('token', result['token']);
      }
    } else {
      print("Already");
    }
  }


}