import os
import jwt
from flask import Flask, render_template, request, Response, g
from flask_socketio import SocketIO

from authentication import token_required
from database import select_db, insert_db

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/')
def index():
    return 200


@app.route('/api/register', methods=['POST'])
def register():
    try:
        key = request.json.get('key')
        serial = request.json.get('serial')

        if select_db('SELECT serial FROM user_info WHERE serial=? AND key=?', (serial, key), one=True) is None:
            result = insert_db('INSERT INTO user_info (serial, key) values (?, ?)', (serial, key))
            if result:
                return {'status': 'Success!!'}, 200
            else:
                return {'status': 'The value you entered is invalid...'}, 400
        else:
            return {'status': 'Already have'}, 400
    except:
        return Response(status=400)


@app.route('/api/login', methods=['GET'])
def login():
    try:
        key = request.json.get('key')
        serial = request.json.get('serial')

        if select_db('SELECT serial FROM user_info WHERE serial=? AND key=?', (serial, key), one=True) is not None:
            enc = jwt.encode({'serial': serial}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            return {'status': 'Login Success!!', 'token': enc}, 200
        else:
            return {'status': 'Login Failed..'}, 400
    except Exception as e:
        return Response(status=400)


@app.route('/api/status', methods=['POST'])
@token_required
def status():
    current_serial = getattr(g, 'get_jwt', 'Null')['serial']
    current_key = select_db('SELECT key FROM user_info WHERE serial=?', (current_serial,), one=True)[0]
    return f"{current_key}, user authenticated"


@app.route('/api/location', methods=['POST'])
@token_required
def location():
    jwt = request.headers.get('Authorization')[7:]
    print(jwt)
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


@socketio.on('location receiver')
def on_receiver(json):
    print('received my event: ' + str(json))
    insert_db("INSERT INTO location (jwt, latitude, longitude) VALUES (?, ?, ?)",
              (request.headers.get('Authorization')[7:], json['latitude'], json['longitude']))

    socketio.emit('my_response', json, callback=messageReceived)


app.config['JWT_SECRET_KEY'] = 'ABCDEFG'
app.config['SECRET_KEY'] = os.urandom(24)

if __name__ == "__main__":
    socketio.run(app, port=80, debug=True)
