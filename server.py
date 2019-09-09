from __future__ import print_function # In python 2.7
import sys
import base64, hashlib, re, sys
import random, string
import psycopg2
import datetime
import json

from hashlib import pbkdf2_hmac as pbkdf2
from os import urandom

from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)

@app.route("/")
def hello():
    message = "Hello"
    return render_template('index.html', message=message)

@app.route("/b")
def b():
    message = "Hello"
    return render_template('b.html', message=message)
        
@app.route('/getsecuritydetails', methods=['GET', 'POST'])
def getsecuritydetails():
    conn = None
    userid = request.form['userid']
    try:
        conn = psycopg2.connect(host="54.172.88.177", database="beiweproject", user="beiweuser", password="password")
        cur = conn.cursor()

        cur.execute("SELECT question, answer FROM database_participant WHERE patient_id like '" + userid + "';")
        both = cur.fetchone()
        print(both, file=sys.stderr)
        question = both[0]
        answer = both[1]

        conn.commit()
        cur.close()

        return json.dumps({'question': question, 'answer': answer})
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return "An Error has Occured1"
        
@app.route('/insert', methods=['POST'])
def insert():
    conn = None
    new_patient_id = None
    password = None
    try:
        conn = psycopg2.connect(host="54.172.88.177", database="beiweproject", user="beiweuser", password="password")
        cur = conn.cursor()
    
        cur.execute('SELECT patient_id FROM database_participant ORDER BY id DESC LIMIT 1')

        last_patient_id = cur.fetchone()[0]
        last_patient_id = int(last_patient_id[2:]) + 1
        new_patient_id = "SG"
        length = len(new_patient_id + str(last_patient_id))
        while length < 7:
            new_patient_id = new_patient_id + "0"
            length = length + 1
        new_patient_id = new_patient_id + str(last_patient_id)
      
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']
        zipcode = request.form['zip']
        state = request.form['state']
        street = request.form['street']
        question = request.form['question']
        answer = request.form['answer']

        password = generate_easy_alphanumeric_string()
        password_hash, salt = generate_user_hash_and_salt( password )
      
        cur_time = datetime.datetime.now()
        user_agent = request.headers.get('User-Agent')
      
        insert_sql = "INSERT INTO database_participant (study_id, salt, deleted, created_on, last_updated, os_type, device_id, patient_id, password, first_name, last_name, email, phone, city, state, zip, street, question, answer) VALUES ('2', '" + salt + "', 'false', '" + str(cur_time) + "', '" + str(cur_time) + "', '', '', '" + new_patient_id + "', '" + password_hash + "', '" + first_name + "', '" + last_name + "', '" + email + "', '" + phone + "', '" + city + "', '" + state + "', '" + zipcode + "', '" + street + "', '" + question + "', '" + answer + "');"
      
        cur.execute(insert_sql)
      
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    return render_template('success.html', user_id=new_patient_id, password=password)
    #return redirect("http://ec2-18-207-173-158.compute-1.amazonaws.com/success.html?response=true&userid=" + new_patient_id + "&pass=" + password)

def device_hash( data ):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return encode_base64( sha256.digest() )

def encode_base64(data):
    return base64.urlsafe_b64encode(data).replace("\n","")

def generate_user_hash_and_salt(password):
    salt = encode_base64(urandom(16))
    password = device_hash(password)
    password_hashed = encode_base64(pbkdf2('sha1', password, salt, iterations=1000, dklen=32))
    return password_hashed, salt

def generate_easy_alphanumeric_string():
    return ''.join(random.choice(string.ascii_lowercase + '123456789') for _ in range(8))

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=80)