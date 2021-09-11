from functools import wraps

import jwt

from flask import request, current_app, Response, g
from flask_socketio import disconnect

from database import select_db


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            access_token = request.headers.get('Authorization').split("Bearer ")[1]
            g.get_jwt = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            try:
                if select_db('SELECT serial FROM user_info WHERE serial=?', [g.get_jwt['serial']], one=True) is None:
                    disconnect()
                    return Response(status=401)
            except Exception as e:
                print(e)
                disconnect()
                return Response(status=401)
        except Exception as e:
            print(e)
            disconnect()
            return Response(status=400)
        return f(*args, **kwargs)

    return decorated
