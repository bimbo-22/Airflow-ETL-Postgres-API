from fastapi import FastAPI
from psycopg2.extras import RealDictCursor
import psycopg2
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

# initialize app
app = FastAPI()

# DB settings from the .env file
DB_SETTINGS = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'postgres',  # Use the correct host for your Docker container
    'port': 5432
}

@app.get("/apod_data")
def get_apod_data():
    try:
        # Establish DB connection
        conn = psycopg2.connect(**DB_SETTINGS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Correct query execution
        cursor.execute("SELECT * FROM apod_data;")
        
        # Fetch data
        data = cursor.fetchall()
        
        # Return data as JSON
        return {'data': data}
        
    except Exception as e:
        return {'error': str(e)}
        
    finally:
        if conn:
            conn.close()
