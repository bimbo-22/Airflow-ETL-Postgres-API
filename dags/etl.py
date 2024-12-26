from airflow import DAG
from airflow.decorators import task 
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import json

# define dag 
with DAG(
    dag_id = 'nasa_apod_postgres',
    start_date = days_ago(1),
    schedule_interval = '@daily',
    catchup = False
) as dag: 
    
    # step 1 : Create table in postgres if it dosen't exist
    @task
    def create_table():
        # initialise the PostgresHook
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
        
        # SQL quert to create a table 
        create_table_query = """
        CREATE TABLE IF NOT EXISTS apod_data(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            explanation TEXT,
            url TEXT,
            date DATE,
            media_type VARCHAR(50)
        );
        
        """
        # Excecute table creation query
        postgres_hook.run(create_table_query)
    
    # step 2 : Extract the NASA API Data(APOD) - Astronomy Picture of the Day [Extract pipleline]
    extract_apod = SimpleHttpOperator(
        task_id = 'extract_apod',
        http_conn_id = 'nasa_api', # connection ID Defined in Airflow for NASA API
        endpoint = 'planetary/apod', # NASA API endpoint for APOD
        method = "GET",
        data = {"api_key":"{{conn.nasa_api.extra_dejson.api_key}}"}, # uisng api key from connection
        response_filter = lambda response:response.json(), # convert response to json
    )
    # step 3 : Transform data (pick necessary info i want to save)
    @task
    def transform_apod_data(response):
        apod_data = {
            'title' : response.get('title', ''),
            'explanation' : response.get('explanation', ''),
            'url' : response.get('url', ''),
            'date' : response.get('date', ''),
            'media_type' : response.get('media_type', '')
            
        }
        return apod_data
    
    # step 4 : Load the data into postgres SQL
    @task
    def load_data_to_postgres(apod_data):
        # initialize the PostgresHook
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
        
        ## define sql insert query
        insert_query = """ 
        INSERT INTO apod_data (title,explanation,url,date,media_type)
        VALUES (%s,%s,%s,%s,%s)
        """
        
        # Excecute sql query 
        postgres_hook.run(insert_query,parameters=(
            apod_data['title'],
            apod_data['explanation'],
            apod_data['url'],
            apod_data['date'],
            apod_data['media_type']
        ))
    # step 5 : Verify data DBViewer
    
    # step 6 : Define the task dependencies
    #Extract
    create_table() >> extract_apod ## Ensure table is created before extraction
    api_response = extract_apod.output
    # Transform
    transformed_data = transform_apod_data(api_response)
    # load
    load_data_to_postgres(transformed_data)