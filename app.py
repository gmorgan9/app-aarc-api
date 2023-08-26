


from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)

# Database connection parameters
db_params = {
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT")
}

def connect_to_database():
    return psycopg2.connect(**db_params)

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'message': 'This is JSON data from your Flask API!',
        'status': 'success'
    }
    return jsonify(data)

@app.route('/api/login', methods=['POST'])
def login():
    # Get user input from the request
    data = request.get_json()
    work_email = data.get('work_email')
    password = data.get('password')

    # Check user credentials in the database
    try:
        conn = connect_to_database()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT * FROM user WHERE work_email = %s AND password = %s", (work_email, password))
        user = cursor.fetchone()

        if user:
            return jsonify({'message': 'Login successful', 'status': 'success'})
        else:
            return jsonify({'message': 'Invalid username or password', 'status': 'error'})
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'status': 'error'})
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)