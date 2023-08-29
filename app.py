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

# USER API

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
        response = make_response(jsonify({'access_token': f'{access_token}'}))

        # Set the access token in an HTTP-only cookie
        response.set_cookie('access_token', value=access_token, httponly=True, secure=True, samesite='Strict')  # Updated here

        return response

    return jsonify({'message': 'Login failed-api'}), 401


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
        # Execute a SQL query to fetch user details
        cursor.execute("SELECT * FROM users WHERE work_email = %s", (current_user,))
        
        # Fetch the user details
        user_details = cursor.fetchone()

        if user_details:

            # Convert the result to a dictionary for JSON serialization
            cursor.execute("SELECT company_name FROM company WHERE company_id = %d" % user_details[9])
            cn = cursor.fetchone()

            user_dict = {
                'user_id': user_details[0],
                'first_name': user_details[1],
                'last_name': user_details[2],
                'work_email': user_details[3],
                'job_title': user_details[5],
                'account_type': user_details[6],
                'company_name': cn[0]
            }
            
            print("User details fetched successfully.")
            return jsonify(user_dict)
        else:
            print("User not found in the database.")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'An error occurred'}), 500

# END USER API

# AUDIT API

# Define SQL statements for each section
section_queries = {
    'CC1': "SELECT * FROM audit_controls WHERE section_number = 'CC1';",
    'CC2': "SELECT * FROM audit_controls WHERE section_number = 'CC2';",
    'CC3': "SELECT * FROM audit_controls WHERE section_number = 'CC3';",
    # Add more sections as needed
}

@app.route('/api/audit-controls', methods=['GET'])
def get_audit_controls():
    try:
        # Get the section requested by the client from the query parameter
        section_requested = request.args.get('section')

        # Check if the requested section is valid
        if section_requested in section_queries:
            # Execute the corresponding SQL query for the requested section
            cursor.execute(section_queries[section_requested])
            
            # Fetch all audit controls for the section
            audit_controls = cursor.fetchall()

            audit_controls_list = []

            for control in audit_controls:
                control_section = control[2] + "." + control[3]  # Clarify how you want to combine these

                audit_controls_dict = {
                    'scope_category': control[1],
                    'section_number': control[2],
                    'control_number': control[3],
                    'control_section': control_section,
                    'point_of_focus': control[4],
                    'control_activity': control[5]
                }
                
                audit_controls_list.append(audit_controls_dict)
            
            return jsonify(audit_controls_list)
        else:
            return jsonify({'error': 'Invalid section requested'}), 400

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Unable to read DB - Audit Controls'}), 500

# END AUDIT API


if __name__ == '__main__':
    app.run(debug=False, host='100.118.102.62', port=5000)
