import os
import jwt
import firebase_admin
from flask import Flask, request, Response, g
from flask_socketio import SocketIO
from firebase_admin import credentials, messaging

from authentication import token_required
from database import select_db, insert_db

cred = credentials.Certificate("C:\\Users\\Administrator\\PycharmProjects\\2021_IoT_Challenge\\firebase.json")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
firebase = firebase_admin.initialize_app(cred)

@app.route('/')
def index():
    return 200


@app.route('/api/register', methods=['POST'])
def register():
    try:
        key = request.json.get('key')
        serial = request.json.get('serial')
        token = request.json.get('token')

        if select_db('SELECT serial FROM user_info WHERE serial=? OR key=?', (serial, key), one=True) is None:
            result = insert_db('INSERT INTO user_info (serial, key, firebase) values (?, ?, ?)', (serial, key, token))
            if result:
                return {'status': 'Success!!'}, 200
            else:
                return {'status': 'The value you entered is invalid...'}, 406
        else:
            return {'status': 'Already have'}, 406
    except Exception as e:
        print(e)
        return Response(status=400)


@app.route('/api/login', methods=['POST'])
def login():
    try:
        key = request.json.get('key')
        serial = request.json.get('serial')

        if select_db('SELECT serial FROM user_info WHERE serial=? AND key=?', (serial, key), one=True) is not None:
            enc = jwt.encode({'serial': serial}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            return {'status': 'Login Success!!', 'token': enc}, 200
        else:
            return {'status': 'Login Failed..'}, 406
    except Exception as e:
        print(e)
        return Response(status=400)


@app.route('/api/status', methods=['GET'])
@token_required
def status():
    current_serial = getattr(g, 'get_jwt', 'Null')['serial']
    current_key = select_db('SELECT key FROM user_info WHERE serial=?', (current_serial,), one=True)[0]
    return f"{current_key}, user authenticated"


@app.route('/api/location', methods=['GET'])
@token_required
def location():
    jwt = request.headers.get('Authorization')[7:]
    lo = select_db('SELECT latitude, longitude, last_timestamp FROM location WHERE jwt=? ORDER BY '
                   'last_timestamp DESC LIMIT 1;', [jwt], one=True)
    if lo is None:
        api = {'status': 400}
    else:
        api = {'status': 200, 'latitude': lo[0], 'longitude': lo[1], 'last_timestamp': lo[2]}
    return api


@socketio.on('connect')
@token_required
def connect_handler():
    get_jwt = getattr(g, 'get_jwt', 'Null')['serial']
    socketio.emit('my_response',
                  {'message': f'{get_jwt} has joined'},
                  broadcast=True)


def messageReceived():
    print('message was received!!!')


@socketio.on('status receiver')
def on_status(json):
    print('received my event: ' + str(json))
    get_serial = jwt.decode(request.headers.get('Authorization')[7:], app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['serial']
    _token = select_db('SELECT firebase FROM user_info WHERE serial=?;', (get_serial,), one=True)[0]
    message = messaging.Message()
    emergency = {'emergency': False}
    if json['status'] is True:
        emergency['emergency'] = True
        message = messaging.Message(
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    title='?????? ??????!!!!',
                    body='???????????? ????????? ?????????????????????!!',
                    icon='',
                    color='#E60505',
                    sound='normal'
                ),
            ),
            data={'detect': 'true'},
            token=_token
        )
        messaging.send(message)

    if json['cnt'] == 1:
        emergency['emergency'] = False
        message = messaging.Message(
            data={'detect': 'false'},
            token=_token
        )
        messaging.send(message)
        # message = messaging.Message(
        #     android=messaging.AndroidConfig(priority='high'),
        #     data={'detect': False},
        #     token=_token
        # )
    print(json['cnt'])


    socketio.emit('my_response', emergency, callback=messageReceived)


@socketio.on('location receiver')
def on_receiver(json):
    print('received my event: ' + str(json))
    insert_db("INSERT INTO location (jwt, latitude, longitude) VALUES (?, ?, ?)",
              (request.headers.get('Authorization')[7:], json['latitude'], json['longitude']))

    socketio.emit('my_response', json, callback=messageReceived)


app.config['JWT_SECRET_KEY'] = 'ABCDEFG'
app.config['SECRET_KEY'] = os.urandom(24)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
