from flask import Flask, request, jsonify, make_response, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import os
import psycopg2
from dotenv import load_dotenv
from flask_cors import CORS
from flask_session import Session

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Read from .env
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

app.secret_key = os.getenv('APP_SECRET')  # Replace with your secret key
app.config['SESSION_TYPE'] = 'filesystem'  # Choose your session storage method
app.config['SESSION_PERMANENT'] = False  # Session expires when the user closes the browser

# Enable CORS for all routes
CORS(app)
Session(app)

# Connect to the PostgreSQL database using the DATABASE_URL from .env
db_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

# No need for the 'users' dictionary anymore

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    work_email = data.get('work_email')
    password = data.get('password')

    # Query the database for the user
    cursor.execute("SELECT work_email, password FROM users WHERE work_email = %s", (work_email,))
    row = cursor.fetchone()

    if row and bcrypt.check_password_hash(row[1], password):
        # Set logged_in status to 1 for the user
        cursor.execute("UPDATE users SET logged_in = 1 WHERE work_email = %s", (work_email,))
        conn.commit()  # Commit the update

        # Store the access token in the session (cookie)
        session['access_token'] = create_access_token(identity=work_email)
        
        return jsonify({'message': 'Login successful'})

    return jsonify({'message': 'Login failed'}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    
    # Set logged_in status to 0 for the user
    cursor.execute("UPDATE users SET logged_in = 0 WHERE work_email = %s", (current_user,))
    conn.commit()  # Commit the update
    
    # Clear the access token from the session (cookie)
    session.pop('access_token', None)
    
    # Logout is handled by simply not using the JWT token anymore on the client-side.
    return jsonify({'message': 'Logged out'})

@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    # You can query the database to fetch user details here if needed.

    return jsonify({'work_email': current_user, 'message': 'User details fetched'})

if __name__ == '__main__':
    app.run(debug=False, host='100.118.102.62', port=5000)
