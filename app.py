import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask

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
            users = cursor.fetchone()[0]
    return {users}

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)