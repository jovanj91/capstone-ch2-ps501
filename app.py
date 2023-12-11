from flask import Flask , request, make_response, jsonify, send_file
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_security import Security, current_user, login_required, SQLAlchemySessionUserDatastore, permissions_accepted, roles_required
from flask_security.utils import verify_password, hash_password, login_user
from flask_security.forms import LoginForm


from functools import wraps
import jwt, os, datetime, werkzeug
from database import db_session, init_db
from models import User, Role


app = Flask(__name__)
api = Api(app)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config['SECURITY_LOGIN_URL'] = '/login'
app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}
app.config["WTF_CSRF_ENABLED"] = False
app.teardown_appcontext(lambda exc: db_session.close())


user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)


class HelloWorld(Resource):
    def get(self):
        return "<p>Hello, World!</p>"

class RegisterUser(Resource):
    def post(self):
        usernameInput = request.json['user_name']
        useremailInput = request.json['user_email']
        passwordInput = request.json['user_password'].encode('utf-8')

        user = security.datastore.find_user(email= useremailInput)
        if not user:
            security.datastore.create_user(email=useremailInput, password=hash_password(passwordInput), username=usernameInput, roles=["user"])
            db_session.commit()
            try:
                db_session.close()
                return make_response(jsonify(message="Registration successful"), 201)
            except Exception as e:
                db_session.rollback()
                return make_response(jsonify(error="Registration failed", details=str(e)), )
        else:
            return make_response(jsonify(error="Email telah terdaftar" ), 409  )


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




class AllUser(Resource):
    @login_required
    @roles_required('admin')
    def get(self):
        allUser = db_session.query(User).all()
        userlist = []
        for user in allUser:
            userlist.append({
                'id' : user.id,
                'email' :user.email
            })
        return make_response(jsonify({
                'data' : userlist
            }), 201)

api.add_resource(RegisterUser, "/register", methods = ["POST"])
api.add_resource(AllUser, "/allUser",  methods = ["GET"])

with app.app_context():
    init_db()
    print(current_user)
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    # app.run(port='9000', debug=True)
    app.run('0.0.0.0')