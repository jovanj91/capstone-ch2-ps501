from flask import Flask , request, make_response, jsonify, send_file
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_security import Security, SQLAlchemySessionUserDatastore

from functools import wraps
import jwt, os, datetime, werkzeug

from models import Session, create_tables, Users, Roles

app = Flask(__name__)
api = Api(app)

secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key

with app.app_context():
    create_tables()

session = Session()
user_datastore = SQLAlchemySessionUserDatastore(session, Users, Roles)
security = Security(app, user_datastore)

class HelloWorld(Resource):
    def get(self):
        return "<p>Hello, World!</p>"

class RegisterUser(Resource):
    def post(self):
        usernameInput = request.json['user_name']
        useremailInput = request.json['user_email']
        passwordInput = request.json['user_password'].encode('utf-8')

        if usernameInput and passwordInput and useremailInput:
            email = session.query(Users).filter_by(user_email=useremailInput).first()
            if not email:
                defaultUserRole = 2
                newUser = Users(username=usernameInput, email=useremailInput, active=1)

                newUser.set_password(passwordInput)
                session.add(newUser)
                session.commit()
                try:
                    session.close()
                    return make_response(jsonify(message="Registration successful"), 201)
                except Exception as e:
                    session.rollback()
                    return make_response(jsonify(error="Registration failed", details=str(e)), )
            elif email:
                return make_response(jsonify(error="Email telah terdaftar" ), 409  )
            else :
                return make_response(jsonify(error="Gagal Daftar" ), 409  )


def token_requried(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token :
            return make_response(jsonify({'message': 'Token is missing'}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'message': 'Token isexpired'}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({'message': 'Invalid Token'}), 401)
        return f(data, *args, **kwargs)
    return decorated

class LoginUser(Resource):
    def post(self):
        useremailInput = request.json['user_email']
        passwordInput = request.json['user_password'].encode('utf-8')

        user = session.query(Users).filter_by(user_email=useremailInput).first()
        if user and user.check_password(passwordInput):
            #generate JWT token
            token = jwt.encode({
                'username' : user.user_name,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            }, app.config['SECRET_KEY'], algorithm ='HS256')

            return make_response(jsonify({
                'username' : user.user_name,
                'message' :"Login Success",
                'token' : token
            }), 201)
        else :
            return make_response(jsonify(message="Login Failed"), 401)


api.add_resource(RegisterUser, "/register", methods = ["POST"])
api.add_resource(LoginUser, "/login", methods = ["POST"])

if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    # app.run(port='9000', debug=True)
    app.run('0.0.0.0')