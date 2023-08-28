# Import the necessary modules
from flask import Flask, request, jsonify, session, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import os
import psycopg2
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Read from .env
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

app.secret_key = os.getenv('APP_SECRET')  # Replace with your secret key
app.config['SESSION_TYPE'] = 'filesystem'  # Choose your session storage method
app.config['SESSION_PERMANENT'] = False  # Session expires when the user closes the browser

# Enable CORS with credentials (allow cookies)
CORS(app, supports_credentials=True)

# Connect to the PostgreSQL database using the DATABASE_URL from .env
db_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

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

        access_token = create_access_token(identity=work_email)

        # Create a response object
        response = make_response(jsonify({'message': f'{access_token}'}))

        # Set the access token in an HTTP-only cookie
        response.set_cookie('access_token', value=access_token, httponly=True, secure=True, samesite='Strict')  # Updated here

        return response

    return jsonify({'message': 'Login failed'}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()

    # Set logged_in status to 0 for the user
    cursor.execute("UPDATE users SET logged_in = 0 WHERE work_email = %s", (current_user,))
    conn.commit()  # Commit the update

    # Logout is handled by simply not using the JWT token anymore on the client-side.

    # Create a response object
    response = make_response(jsonify({'message': 'Logged out'}))

    # Remove the access token by setting an empty token with an expired date
    response.set_cookie('access_token', value='', expires=0, httponly=True, secure=True, samesite='Strict')  # Updated here

    return response
    
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    print(f"User {current_user} is trying to access user details.")
    
    try:
        # You can query the database to fetch user details here if needed.

        print("User details fetched successfully.")
        return jsonify({'work_email': current_user, 'message': 'User details fetched'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'An error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='100.118.102.62', port=5000)
