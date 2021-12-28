# -*- coding: utf-8 -*-

#Created on Sun Dec 26 18:08:45 2021

#author: Pavlos Nikolaos Toumlelis


import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, render_template, flash, request, Markup, session, Response, send_file
from flask_mail import Mail, Message
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import time, os, sys
import datetime
from flask_cors import CORS, cross_origin
import json
import csv
import random

# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose e_diabetes database
db = client['e_diabetes']
#choose the users collection
users = db['users']
#choose the patient_data collection
patient_data = db['patient_data']

# App config.
app = Flask(__name__, static_url_path='',
            static_folder='templates',
            template_folder='templates')
DEBUG = True
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
CORS(app)

mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'XXX'
app.config['MAIL_PASSWORD'] = 'XXX'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/")
@cross_origin()
def home():
    return render_template("login.html")

#this is the endpoint for registering into the platform
@app.route("/signup",methods=['GET', 'POST'])
@cross_origin()
def signup():
    if request.method == 'GET':
        firstName = request.args.get('firstName')
        lastName = request.args.get('lastName')
        username = request.args.get('username')
        email = request.args.get('email')
        password = request.args.get('password')
        userType = request.args.get('userType')
        existingUser = users.find({'username':username})

        if existingUser.count() !=0 :
            return Response('{"status":"anotheruser"}', status=500, mimetype="application/json")
        else:
            users.insert_one({'firstName': firstName,'lastName': lastName,'username': username,
                                  'email': email, 'password':password, 'userType':userType})
            return Response('{"status":"success"}', status=200, mimetype="application/json")
    return Response('{"status":"error"}', status=500, mimetype="application/json")

#this is the endpoint for logging into the platform
@app.route('/signin',methods=['GET', 'POST'])
@cross_origin()
def signin():
    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')
        existingUser = users.find({'username':username,'password':password})
        doctorCategory = users.find({'username':username,'userType':'doctor'})
        patientCategory = users.find({'username':username,'userType':'patient'})

        #check if the user exists and the user type (doctor or patient)
        if existingUser.count() !=0 and doctorCategory.count()!=0:
            response_data = {'username': str(username), 'userType':'doctor'}
            return Response(json.dumps(response_data), status=200, mimetype="application/json")
        elif existingUser.count() !=0 and patientCategory.count()!=0:
            response_data = {'username': str(username), 'userType':'patient'}
            return Response(json.dumps(response_data), status=200, mimetype="application/json")
        else:
            return Response('{"userType":"nonexistent"}', status=500, mimetype="application/json")
    return Response('{"userType":"nonexistent"}', status=500, mimetype="application/json")

@app.route("/sendemail")
def sendemail():
   username = request.args.get('username')
   doctor_found = users.find({'username':username},{"email": 1, "_id":0})
   doctor_found_list_cur = list(doctor_found)
   doctor_email = doctor_found_list_cur[0].get("email")
   msg = Message('Hello', sender = 'XXX', recipients = [doctor_email])
   msg.body = "Hello Flask message sent from Flask-Mail"
   mail.send(msg)
   return "Sent"


#this is the endpoint for importing patient's data from patient's view
@app.route('/data_import',methods=['GET', 'POST'])
@cross_origin()
def data_import():
    if request.method == 'GET':
        #get the needed arguments (Glucose,BloodPressure,Insulin,BMI,Age)
        Glucose = request.args.get('Glucose')
        BloodPressure = request.args.get('BloodPressure')
        Insulin = request.args.get('Insulin')
        BMI = request.args.get('BMI')
        Age = request.args.get('Age')

#patient will now import their current data
Glucose=int(input('Type your current glucose level\t'))
BloodPressure=int(input('Type your current BloodPressure\t'))
BMI=float(input('Type your current bmi level\t'))
Age=int(input("Type your age\t"))
Insulin=int(input('Type your insulin level two hours after glucose administration\t'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


