import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)

@app.get("/")
def home():
    return "hello world"

if __name__ == '__main__':
    app.run(debug=True, host='100.118.102.62', port=5000)