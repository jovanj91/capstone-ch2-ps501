from flask import Flask , request, make_response, jsonify, send_file
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_security import Security, current_user, login_required, SQLAlchemySessionUserDatastore, permissions_accepted, roles_required
from flask_security.utils import verify_password, hash_password, login_user

from functools import wraps
import jwt, os, datetime, werkzeug
from database import db_session, init_db
from models import User, Role, RolesUsers, StuntCheck, ChildrenData

# import random
# import numpy as np
# import tensorflow as tf
# from sklearn.preprocessing import StandardScaler, LabelEncoder
# import pandas as pd

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
            return make_response(jsonify(error="Data failed to be added", details=str(e)), 409)

class GetChildrenData(Resource):
    @login_required
    @roles_required('user')
    def get(self):
        children = db_session.query(ChildrenData).filter(ChildrenData.user_id == current_user.id)
        childrenList = []
        for child in children:
            stuntCheck = db_session.query(StuntCheck).filter(StuntCheck.child_id == child.id).order_by(StuntCheck.checked_at.desc()).first()
            if stuntCheck != None :
                lastCheck = stuntCheck.checkResult
            else :
                lastCheck = "Not Checked Yet"
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
    def post(self):
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

# class StuntingChecking(Resource):
#     @login_required
#     @roles_required('user')
#     def post(self):
#         child_id = request.json['child_id']
#         weight = request.json['weight']
#         height = request.json['height']
#         age = request.json['age']
#         bmi = request.json['bmi']
#         checkedAt = request.json['checked_at']
#         childData = db_session.query(ChildrenData).filter(ChildrenData.id == child_id).first()
#         gender = childData.gender
#         #check stunting
#         df = pd.read_csv('./Stunting Datasets.csv', delimiter=';')

#         group_counts = df.groupby(['Age', 'Gender', 'Category']).size().reset_index(name='Count')

#         train_ratio = 0.7
#         val_ratio = 0.2

#         train_counts = (group_counts['Count'] * train_ratio).astype(int)
#         val_counts = (group_counts['Count'] * val_ratio).astype(int)

#         train_data = pd.DataFrame()
#         val_data = pd.DataFrame()

#         for i, row in group_counts.iterrows():
#             subset = df[(df['Age'] == row['Age']) & (df['Gender'] == row['Gender']) & (df['Category'] == row['Category'])]
#             train_data = pd.concat([train_data, subset.head(train_counts[i])], ignore_index=True)
#             val_data = pd.concat([val_data, subset.head(val_counts[i])], ignore_index=True)

#         label_encoder = LabelEncoder()
#         train_data['Category'] = label_encoder.fit_transform(train_data['Category'])
#         val_data['Category'] = label_encoder.transform(val_data['Category'])

#         X_train = train_data[['Age', 'Gender', 'Height', 'Weight', 'BMI']]
#         y_train = train_data['Category']
#         X_val = val_data[['Age', 'Gender', 'Height', 'Weight', 'BMI']]
#         y_val = val_data['Category']

#         scaler = StandardScaler()
#         X_train = scaler.fit_transform(X_train)
#         X_val = scaler.transform(X_val)

#         model = tf.keras.models.load_model('./saved_model')

#         test_data = np.array([[age, gender, height, weight, bmi]])

#         scaled_test = scaler.transform(test_data)

#         predict = model.predict(scaled_test)

#         result = "Normal" if predict[0,0] <= 0.5 else "Stunting"

#         inputData = StuntCheck(age=age, weight=weight, height=height, bodyMassIndex=bmi, checkResult=result, checked_at=checkedAt, child=childData)
#         checkResult = []
#         checkResult.append({
#             'firstname' : childData.first_name,
#             'lastname' : childData.last_name,
#             'gender' : gender,
#             'weight' : weight,
#             'height' : height,
#             'age' : age,
#             'bmi' : bmi,
#             'checkResult' : result,
#             'checkedAt' : checkedAt,})
#         db_session.add(inputData)
#         db_session.commit()
#         try:
#             db_session.close()
#             return make_response(jsonify({'data' : checkResult, 'message' : 'Child Checked Succesfully'}), 201)
#         except Exception as e:
#             db_session.rollback()
#             return make_response(jsonify(error="Child failed to checked", details=str(e)), 409)


api.add_resource(HelloWorld, "/", methods = ["GET"])
api.add_resource(RegisterUser, "/register", methods = ["POST"])
#login API already handled with Flask_security
api.add_resource(AllUser, "/allUser",  methods = ["GET"])
api.add_resource(InputChildData, "/inputChildData",  methods = ["POST"])
api.add_resource(GetChildrenData, "/getChildrenData",  methods = ["GET"])
api.add_resource(GetChildCheckHistory, "/getChildHistory",  methods = ["POST"])
# api.add_resource(StuntingChecking, "/stuntingCheck",  methods = ["POST"])

with app.app_context():
    init_db()

if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host="127.0.0.1", port=8080)