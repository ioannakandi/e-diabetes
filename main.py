# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 11:48:35 2021

@author: kostis mavrogiorgos
"""

import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, render_template, flash, request, Markup, session, Response, send_file
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

# App config.
app = Flask(__name__, static_url_path='', 
            static_folder='templates',
            template_folder='templates')
DEBUG = True
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
CORS(app)

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
        #in this array the data will be stored (in case of a patient)
        data = []
        
        if existingUser.count() !=0 : 
            return Response('{"status":"anotheruser"}', status=200, mimetype="application/json")
        else:
            users.insert_one({'firstName': firstName,'lastName': lastName,'username': username,
                                  'email': email, 'password':password, 'userType':userType, 'data': data})
            return Response('{"status":"success"}', status=200, mimetype="application/json")       
    return Response('{"status":"error"}', status=500, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)