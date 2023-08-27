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

    # validate the received values
    if _work_email and _password:
        # check if the user exists
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
          
        sql = "SELECT * FROM users WHERE work_email=%s"
        sql_where = (_work_email,)
          
        cursor.execute(sql, sql_where)
        row = cursor.fetchone()

        if row:
            user_id = row['user_id']  # Assuming you have a user ID in your table
            stored_password_hash = row['password']
            
            if check_password_hash(stored_password_hash, _password):
                # Update the user's 'logged_in' status to 1
                update_cursor = conn.cursor()
                update_sql = "UPDATE users SET logged_in = 1 WHERE user_id = %s"
                update_cursor.execute(update_sql, (user_id,))
                conn.commit()
                update_cursor.close()
                
                session['work_email'] = _work_email
                session['user_id'] = user_id
                cursor.close()
                return jsonify({'message': 'You are logged in successfully'})
            else:
                resp = jsonify({'message': 'Bad Request - invalid password'})
                resp.status_code = 400
                return resp
    else:
        resp = jsonify({'message': 'Bad Request - invalid credentials'})
        resp.status_code = 400
        return resp

    
@app.route('/logout', methods=['GET'])
def logout():
    # Get the user_id from the query parameters
    user_id = request.args.get('user_id')

    if user_id:
        # Assuming you have a 'logged_in' column in your 'users' table
        update_cursor = conn.cursor()
        update_sql = "UPDATE users SET logged_in = 0 WHERE user_id = %s RETURNING work_email"
        update_cursor.execute(update_sql, (user_id,))
        updated_user = update_cursor.fetchone()
        
        if updated_user:
            # Extract the 'work_email' from the tuple
            work_email = updated_user[0]

            # Clear the session data for the logged-out user
            session.pop('work_email', None)
            
            conn.commit()
            update_cursor.close()
            return jsonify({'message': f'User {work_email} successfully logged out'})
        else:
            update_cursor.close()
            return jsonify({'message': 'Logout failed. User not found or not logged in.'}), 400

    # If the user_id is not provided or if there are errors, you can handle it accordingly
    return jsonify({'message': 'Logout failed. Please provide a valid user_id.'}), 400





if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)
