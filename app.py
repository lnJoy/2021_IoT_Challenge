import os
import bcrypt
from flask import Flask, request, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager, create_access_token

from models import db, User

app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register():
    try:
        # imei = bcrypt.hashpw(newuser['imei'].encode('utf-8'), bcrypt.gensalt())
        imei = request.json.get('imei')
        serial = request.json.get('serial')
        newuserinfo = User(serial=serial, imei=imei)

        if User.query.filter_by(serial=serial).first() is None:
            db.session.add(newuserinfo)
            db.session.commit()

        payload = jsonify({
            'imei': imei,
            'serial': serial
        })

        print(serial)

        access_token = create_access_token(serial)
        print(access_token)
        return jsonify(access_token=access_token)
        # return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=401)


@app.route('/status', methods=['POST'])
@jwt_required()
def location():
    current_user = get_jwt_identity()

    return f"{current_user}, user authenticated"


basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'IoS.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwtest'
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)
db.app = app
db.create_all()

jwt = JWTManager(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
