import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify

GET_USERS = """SELECT * FROM users;"""

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get("/")
def home():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_USERS)
            users_data = cursor.fetchall()  # Fetch all user data
    users_list = []
    for user in users_data:
        user_dict = {
            "user_id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "work_email": user[3],
            # Add more fields as needed
        }
        users_list.append(user_dict)
    return jsonify({"users": users_list})

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)