from flask import Flask, jsonify, request, session
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets
from flask_cors import CORS
from datetime import timedelta

import psycopg2 
import psycopg2.extras


app = Flask(__name__)
CORS(app)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)
app.secret_key = secrets.token_hex(16)

load_dotenv()

# Access environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)

@app.route('/')
def home():
    passhash = generate_password_hash('cairocoders')
    print(passhash)
    if 'work_email' in session:
        work_email = session['work_email']
        return jsonify({'message' : 'You are already logged in', 'work_email' : work_email})
    else:
        resp = jsonify({'message' : 'Unauthorized'})
        resp.status_code = 401
        return resp
    
@app.route('/login', methods=['POST'])
def login():
    _json = request.json
    _work_email = _json['work_email']
    _password = _json['password']
    print(_password)
    # validate the received values
    if _work_email and _password:
        #check user exists          
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
          
        sql = "SELECT * FROM users WHERE work_email=%s"
        sql_where = (_work_email,)
          
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        work_email = row['work_email']
        password = row['password']
        if row:
            if check_password_hash(password, _password):
                session['work_email'] = work_email
                cursor.close()
                return jsonify({'message' : 'You are logged in successfully'})
            else:
                resp = jsonify({'message' : 'Bad Request - invalid password'})
                resp.status_code = 400
                return resp
    else:
        resp = jsonify({'message' : 'Bad Request - invalid credendtials'})
        resp.status_code = 400
        return resp
    
@app.route('/logout')
def logout():
    if 'work_email' in session:
        session.pop('work_email', None)
    return jsonify({'message' : 'You successfully logged out'})


if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)
