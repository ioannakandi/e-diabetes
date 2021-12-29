# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 18:42:09 2021

@author: Ioanna Kandi
"""

import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, render_template, flash, request, Markup, session, Response, send_file
import time, os, sys
import datetime
from datetime import datetime
from flask_cors import CORS, cross_origin
import json
import csv
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

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
        
        



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)