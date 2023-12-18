from flask import Flask , request, make_response, jsonify, send_file
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_security import Security, current_user, login_required, SQLAlchemySessionUserDatastore, permissions_accepted, roles_required
from flask_security.utils import verify_password, hash_password, login_user
from flask_security.forms import LoginForm


from functools import wraps
import jwt, os, datetime, werkzeug
from database import db_session, init_db
from models import User, Role, RolesUsers, StuntCheck


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config['SECURITY_LOGIN_URL'] = '/login'
app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}
app.config["WTF_CSRF_ENABLED"] = False
app.teardown_appcontext(lambda exc: db_session.close())


user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)


class HelloWorld(Resource):
    @login_required
    def get(self):
        return f"<p>Hello, World! {current_user.username}</p>"

class RegisterUser(Resource):
    def post(self):
        usernameInput = request.json['username']
        useremailInput = request.json['email']
        passwordInput = request.json['password'].encode('utf-8')

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
            return make_response(jsonify(error="Email already registered" ), 409  )


class AllUser(Resource):
    @login_required
    @roles_required('admin')
    def get(self):
        allUser = db_session.query(User).join(RolesUsers).filter(RolesUsers.role_id == 2)
        userlist = []
        for user in allUser:
            userlist.append({
                'id' : user.id,
                'email' :user.email
            })
        return make_response(jsonify({
                'data' : userlist
            }), 201)

class InputData(Resource):
    @login_required
    @roles_required('user')
    def post(self):
        nameInput = request.json['name']
        ageInput = request.json['age']
        genderInput = request.json['gender']
        heightInput = request.json['height']
        weightInput = request.json['weight']
        bmiInput = request.json['bmi']

        uname = db_session.query(User).filter_by(username=current_user.username).first()
        print(uname)
        print(type(uname))
        inputData = StuntCheck(name=nameInput, age=ageInput, gender=genderInput, height=heightInput, weight=weightInput, bodyMassIndex=bmiInput, user=uname)

        if nameInput and ageInput and genderInput and heightInput and weightInput and bmiInput:
            db_session.add(inputData)
            db_session.commit()
            try:
                db_session.close()
                return make_response(jsonify(message="Data added successfully"), 201)
            except Exception as e:
                db_session.rollback()
                return make_response(jsonify(error="Data failed to be added", details=str(e)), )
        else:
            return make_response(jsonify(message="Please Fill Data Completely"), 404)

api.add_resource(HelloWorld, "/", methods = ["GET"])
api.add_resource(RegisterUser, "/register", methods = ["POST"])
#login API already handled with Flask_security
api.add_resource(AllUser, "/allUser",  methods = ["GET"])
api.add_resource(InputData, "/inputData",  methods = ["POST"])


with app.app_context():
    init_db()

if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host="127.0.0.1", port=8080, debug=True)