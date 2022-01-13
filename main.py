# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 11:48:35 2021

@author: kostis mavrogiorgos
"""

import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, render_template, flash, request, Markup, session, Response, send_file
from flask_mail import Mail, Message
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import time, os, sys
from datetime import datetime
from flask_cors import CORS, cross_origin
import json
import csv
import random
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt       # matplotlib.pyplot plots data
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB # I am using Gaussian algorithm from Naive Bayes

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
app.config['MAIL_USERNAME'] = 'gibm3112@gmail.com'
app.config['MAIL_PASSWORD'] = '20213112!!!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#this is a function to send an email if the blood pressure o a patient is high
def sendemail(doctor, patient, BloodPressure):
   doctor_found = users.find({'username':doctor},{"email": 1, "_id":0})
   doctor_found_list_cur = list(doctor_found)
   doctor_email = doctor_found_list_cur[0].get("email")
   msg = Message('Abnormal Blood Pressure', sender = 'gibm3112@gmail.com', recipients = [doctor_email])
   msg.body = "The blood pressure of the patient "+str(patient)+" is abnormal "+"("+str(BloodPressure)+")"
   mail.send(msg)

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


#this is the endpoint for predicting if a patient will need insulin or not
@app.route('/predict',methods=['GET', 'POST'])
@cross_origin()
def predict():
    if request.method == 'GET':
        #get the needed arguments (Glucose,BloodPressure,Insulin,BMI,Age)
        Glucose = request.args.get('Glucose')
        BloodPressure = request.args.get('BloodPressure')
        Insulin = request.args.get('Insulin')
        BMI = request.args.get('BMI')
        Age = request.args.get('Age')
        #read the dataset that we will use to make the prediction
        pdata = pd.read_csv("diabetes.csv")
        columns = list(pdata)[0:-1] # Excluding Outcome column which is the one we want to predict
        n_true = len(pdata.loc[pdata['Outcome'] == True])
        n_false = len(pdata.loc[pdata['Outcome'] == False])
        #use only the specific columns to train our model
        features_cols = ['Glucose', 'BloodPressure','Insulin', 'BMI', 'Age']
        predicted_class = ['Outcome']
        X = pdata[features_cols].values      # Predictor feature columns (5 X m)
        Y = pdata[predicted_class]. values   # Predicted class (1=True, 0=False) (1 X m)
        split_test_size = 0.30
        x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=split_test_size, random_state=52)
        #Replace 0s with serial mean
        rep_0 = SimpleImputer(missing_values=0, strategy="mean")
        x_train = rep_0.fit_transform(x_train)
        x_test = rep_0.fit_transform(x_test)
        #Train Naive Bayes algorithm
        # Lets creat the model
        diab_model = GaussianNB()
        diab_model.fit(x_train, y_train.ravel())
        #Performance of our model with training data
        diab_train_predict = diab_model.predict(x_train)
        #Performance of our model with testing data
        diab_test_predict = diab_model.predict(x_test)
        # define input (the one that we took from the endpoint parameters)
        new_input = [[Glucose,BloodPressure,Insulin,BMI,Age]]
        #get prediction for new input
        new_output = diab_model.predict(new_input)
        #transform the array of new_output to string and check the value.
        prediction_result = np.array2string(new_output)
        #if it is 0 then return a message that says that the patient does not need insulin. If it is 1 then
        #suggest that the patient needs insulin
        if "0" in prediction_result:
           return Response('{"message":"Based on Naive Bayes ML algorithm, the patient does not need insulin."}', status=200, mimetype="application/json")
        elif "1" in prediction_result:
            return Response('{"message":"Based on Naive Bayes ML algorithm, the patient needs insulin."}', status=200, mimetype="application/json")
        else:
            return Response('{"message":"Please try again."}', status=500, mimetype="application/json")


# endpoint for importing patients' data as a doctor
@app.route("/drDataImport",methods=['GET', 'POST'])
@cross_origin()
def drDataImport():
    if request.method == 'GET':
        username = request.args.get('username')
        age = request.args.get('age')
        bmi = request.args.get('bmi')
        glucose = request.args.get('glucose')
        bloodPressure = request.args.get('bloodPressure')
        insulin = request.args.get('insulin')
        now = datetime.now()
        today = str(now.strftime("%d/%m/%Y %H:%M:%S"))

        existingPatient = users.find({'username':username})

        if existingPatient.count() !=0 :

            patient_data.insert_one({'username': username,'age': int(age),'bmi': int(bmi),'gluose': int(glucose),
                                 'bloodPressure':int(bloodPressure),'insulin': int(insulin),'date': today})


            return Response('{"message":"Data imported successfully!"}', status=200, mimetype="application/json")
        else:
            return Response('{"message":"Oops! Something went wrong. Please try again."}', status=500, mimetype="application/json")





# endpoint for doctor's perscription import
@app.route("/perscriptionImport",methods=['GET', 'POST'])
@cross_origin()
def perscriptionImport():
    if request.method == 'GET':
        username = request.args.get('username')
        perscription = request.args.get('perscription')

        new_perscription = {"$set": {'perscription':perscription}}

        query_cursor=patient_data.update_many({"username":username}, new_perscription)



        #responses for successfull data import or errors respectively
        return Response('{"message":"Perscription imported successfully!"}', status=200, mimetype="application/json")
    return Response('{"message":"Oops! Something went wrong. Please try again."}', status=500, mimetype="application/json") 


#doctor's account management endpoint
@app.route("/drAccountManagement",methods=['GET', 'POST'])
@cross_origin()
def drAccountManagement():
    
    #new data entry 
    if request.method == 'GET':
        old_username = request.args.get('old_username')
        new_username = request.args.get('new_username')
        firstname = request.args.get('firstname')
        lastname = request.args.get('lastname')
        email = request.args.get('email')
        password = request.args.get('password')
        

        
        new_values = { "$set": { 'firstname': firstname,'lastname': lastname,
                                  'email': email, 'password':password, 'username': new_username } }        
        
        query_cursor=users.update_many({"username":old_username}, new_values )
     
        
        #responses for successfull update or errors respectively
        return Response('{"message":"All set! Chages saved successfully."}', status=200, mimetype="application/json")
    return Response('{"message":"Oops! Something went wrong. Please try again."}', status=500, mimetype="application/json") 

# endpoint for retrieving all patients' data in list form
@app.route("/getAllData",methods=['GET', 'POST'])
@cross_origin()
def getAllData():
    if request.method == 'GET':
        #retrieve the data
        query_cursor = patient_data.find({},{"_id": 0})
        # convert cursor object to python list
        list_cur = list(query_cursor)
        return Response(json.dumps(list_cur), status=200, mimetype="application/json")
    return Response('{"message":"Please try again"}', status=500, mimetype="application/json")


#this is the endpoint for importing patient's data from patient's view
@app.route('/data_import',methods=['GET', 'POST'])
@cross_origin()
def data_import():
    if request.method == 'GET':
        #get the needed arguments (Glucose,BloodPressure,Insulin,BMI,Age)
        username = request.args.get('username')
        age = request.args.get('age')
        bmi = request.args.get('bmi')
        glucose = request.args.get('glucose')
        bloodPressure = request.args.get('bloodPressure')
        insulin = request.args.get('insulin')
        now = datetime.now()
        today = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        #check blood pressure and if it is of high value, inform the doctor
        if(int(bloodPressure)>140):
            try:
                sendemail("komav", username, bloodPressure)
            except:
                pass
        patient_data.insert_one({'username': username,'age': int(age),'bmi': int(bmi),'gluose': int(glucose),
                                 'bloodPressure':int(bloodPressure),'insulin': int(insulin),'date': today})
        return Response('{"message" : "imported data is successful"}', status=200, mimetype="application/json")
    
    
# endpoint for prescription view from patient's view
@app.route("/prescriptionView",methods=['GET', 'POST'])
@cross_origin()
def prescriptionView():
#get the needed arguments
    if request.method == 'GET':
        #get the needed arguments (username)
        username = request.args.get('username')
        #retrieve the data
        query_cursor = patient_data.find({"username":username},{"perscription": 1, "_id":0}).limit(1)
        # convert cursor object to python list
        list_cur = list(query_cursor)
        return Response(json.dumps(list_cur), status=200, mimetype="application/json")
    return Response('{"message":"Please try again"}', status=500, mimetype="application/json")

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




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
