from fastapi import FastAPI
from psycopg2.extras import RealDictCursor
import psycopg2
import os
from dotenv import load_dotenv
import uvicorn
from pathlib import Path
env_path = Path(__file__).parent.parent / ".env"

print(env_path)
# load .env file
load_dotenv(dotenv_path=env_path)
# initailise app 
app = FastAPI()

DB_SETTINGS = {
    'dbname' : os.getenv('POSTGRES_DB'),
    'user' : os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'localhost',
    'port' : 5432
    
}
print(DB_SETTINGS)



@app.get("/apod_data")
def get_apod_data():
    conn = None  # Initialize conn to None to avoid UnboundLocalError
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_SETTINGS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("Connected to the database")
        cursor.execute("SELECT * FROM apod_data;")
        data = cursor.fetchall()
        
        return {'data': data}
    except Exception as e:
        return {'error': str(e)}
    finally:
        if conn:  # Ensure conn is closed only if it was successfully initialized
            conn.close()

            
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

