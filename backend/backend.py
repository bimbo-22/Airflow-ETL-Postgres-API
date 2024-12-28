from fastapi import FASTAPI
from psycopg2.extras import RealDictCursor
import psycopg2
import os
from dotenv import load_dotenv


# load .env file
load_dotenv()
# initailise app 
app = FASTAPI()

DB_SETTINGS = {
    'dbname' : os.getenv('POSTGRES_DB'),
    'user' : os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'postgres',
    'port' : 5432
    
}



@app.get("/apod_data")
def get_apod_data():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.excecute("SELECT * FROM apod_data;")
        data = cursor.fetchall()
        return {'data':data}
    except Exception as e:
        return{'error':str(e)}
    finally:
        if conn:
            conn.close()

