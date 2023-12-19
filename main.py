from flask import Flask , request, make_response, jsonify, send_file
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_security import Security, current_user, login_required, SQLAlchemySessionUserDatastore, permissions_accepted, roles_required
from flask_security.utils import verify_password, hash_password, login_user


from functools import wraps
import jwt, os, datetime, werkzeug
from database import db_session, init_db
from models import User, Role, RolesUsers, StuntCheck, ChildrenData

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

class InputChildData(Resource):
    @login_required
    @roles_required('user')
    def post(self):
        firsnameInput = request.json['firstname']
        lastnameInput = request.json['lastname']
        genderInput = request.json['gender']
        dobInput = request.json['dob']
        uname = db_session.query(User).filter_by(username=current_user.username).first()

        inputData = ChildrenData(first_name=firsnameInput, last_name=lastnameInput, child_dob=dobInput, gender=genderInput,  user=uname)

        db_session.add(inputData)
        db_session.commit()
        try:
            db_session.close()
            return make_response(jsonify(message="Data added successfully"), 201)
        except Exception as e:
            db_session.rollback()
            return make_response(jsonify(error="Data failed to be added", details=str(e)), )

class GetChildrenData(Resource):
    @login_required
    @roles_required('user')
    def get(self):
        children = db_session.query(ChildrenData).filter(ChildrenData.user_id == current_user.id)
        childrenList = []
        for child in children:
            lastCheck = db_session.query(StuntCheck).filter(StuntCheck.child_id == child.id).order_by(StuntCheck.checked_at.desc()).first()
            childrenList.append({
                'child_id' : child.id,
                'firstname' : child.first_name,
                'lastname' :child.last_name,
                'gender' : child.gender,
                'dob' : child.child_dob,
                'lastCheck' : lastCheck
            })
        return make_response(jsonify({
            'data' : childrenList
        }), 201)


class GetChildCheckHistory(Resource):
    @login_required
    @roles_required('user')
    def get(self):
        child_id = request.json['child_id']
        histories = db_session.query(StuntCheck).filter(StuntCheck.child_id == child_id)
        historyList = []
        for history in histories:
            historyList.append({
                'weight' : history.weight,
                'height' : history.height,
                'age' : history.age,
                'bmi' : history.bodyMassIndex,
                'checkResult' : history.checkResult,
                'checkedAt' : history.checked_at,
            })
        return make_response(jsonify({
            'data' : historyList
        }), 201)

class StuntingChecking(Resource):
    @login_required
    @roles_required('user')
    def post(self):
        child_id = request.json['child_id']
        weight = request.json['weight']
        height = request.json['height']
        age = request.json['age']
        bmi = request.json['bmi']
        checkedAt = request.json['checked_at']


api.add_resource(HelloWorld, "/", methods = ["GET"])
api.add_resource(RegisterUser, "/register", methods = ["POST"])
#login API already handled with Flask_security
api.add_resource(AllUser, "/allUser",  methods = ["GET"])
api.add_resource(InputChildData, "/inputChildData",  methods = ["POST"])
api.add_resource(GetChildrenData, "/getChildrenData",  methods = ["GET"])
api.add_resource(GetChildCheckHistory, "/getChildHistory",  methods = ["GET"])
api.add_resource(StuntingChecking, "/stuntingCheck",  methods = ["POST"])

with app.app_context():
    init_db()

if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host="127.0.0.1", port=8080, debug=True)