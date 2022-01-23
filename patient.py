# -*- coding: utf-8 -*-

"""

Created on Thu 13 Jan 12:48:16 2022

@author: Pavlos Nikolaos Toumlelis
"""

import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, render_template, flash, request, Markup, session, Response, send_file
from flask_mail import Mail, Message
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from pprint import pprint
import time, os, sys
from datetime import datetime
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
app.config['MAIL_USERNAME'] = 'kostismvg@gmail.com'
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
            users.insert_one({'firstname': firstName,'lastname': lastName,'username': username,
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

#this is a function to send an email if the blood pressure o a patient is high
def sendemail(doctor, patient, BloodPressure):
   doctor_found = users.find({'username':doctor},{"email": 1, "_id":0})
   doctor_found_list_cur = list(doctor_found)
   doctor_email = doctor_found_list_cur[0].get("email")
   msg = Message('Abnormal Blood Pressure', sender = 'kostismvg@gmail.com', recipients = [doctor_email])
   msg.body = "The blood pressure of the patient "+str(patient)+" is abnormal "+"("+str(BloodPressure)+")"
   mail.send(msg)

#this is the endpoint for importing patient's data from patient's view
@app.route('/data_import',methods=['GET', 'POST'])
@cross_origin()
def data_import():

 if request.method == 'GET' :

     #get the needed arguments (Glucose,BloodPressure,Insulin,BMI,Age)
     username = request.args.get('username')
     glucose = request.args.get('glucose')
     bloodPressure = request.args.get('bloodPressure')
     insulin = request.args.get('insulin')
     bmi = request.args.get('bmi')
     age = request.args.get('age')
     now = datetime.now()
     today = str(now.strftime("%d/%m/%Y %H:%M:%S"))

     patient_data.insert_one({'username': username, 'gluose' : int(glucose), 'bloodPressure' : int(bloodPressure),
                              'insulin' : int(insulin), 'bmi' : int(bmi), 'age' : int(age), 'date': today })

     return Response('{"status" : "imported data is successful"}', status=200, mimetype="application/json")

#this is the endpoint for patient account management
@app.route('/PatientAccountManagement',methods=['GET', 'POST'])
@cross_origin()
def PatientAccountManagement():

 if request.method == 'GET' :

     #patient will manage their personal data
        old_username = request.args.get('old_username')
        new_username = request.args.get('new_username')
        firstname = request.args.get('firstname')
        lastname = request.args.get('lastname')
        email = request.args.get('email')
        password = request.args.get('password')

        personalData= { "$set": { 'username': new_username, 'firstname': firstname,
                                      'lastname': lastname, 'email': email, 'password': password }}

        query_cursor=users.update_many ( {"username": old_username}, personalData)

        #responses for successful update or errors respectively
        return Response('{"message":"All set! Changes saved successfully."}', status=200, mimetype="application/json")
 return Response('{"message":"Oops! Something went wrong. Please try again."}', status=500, mimetype="application/json")


# endpoint for prescription view from patient's view
@app.route("/prescriptionView",methods=['GET', 'POST'])
@cross_origin()
def prescriptionView():
#get the needed arguments
    if request.method == 'GET':
      username = request.args.get('username')

      #prescription_view variable finds the patient's perscriptions that doctor have imported.
      #Additionally, maximum limit for prescriptions has been defined to 3
      #conversion in list form is done
      #pprint has been used in order to see the data in easy read format

      prescription_view = patient_data.find( {"username" : username}, { "_id" : 0,  "perscription" : 1}).limit(3)
      list_prescription_view = list(prescription_view)
      for perscription in list_prescription_view:
                pprint(perscription)

      return Response(json.dumps(list_prescription_view), status=200, mimetype="application/json")
      return Response('{"status" : "These are your prescriptions"}', status=200, mimetype="application/json")

#this is the endpoint for patient's data view
@app.route('/patient_dataView',methods=['GET', 'POST'])
@cross_origin()
def patient_dataView():

 if request.method == 'GET' :

     #get the needed arguments
     username = request.args.get('username')

     #data_view variable finds all the patient's imported data except perscription which
     #can be viewed in "Perscription" template
     #conversion in list form is done
     data_view = patient_data.find({"username" : username}, {"_id" : 0, "perscription" : 0})
     list_data_view = list(data_view)

     return Response(json.dumps(list_data_view), status=200, mimetype="application/json")
     return Response('{"status" : "these are all your imported data"}', status=200, mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


