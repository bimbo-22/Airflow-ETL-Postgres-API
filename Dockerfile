FROM quay.io/astronomer/astro-runtime:12.6.0

# Install PostgreSQL development libraries (if needed for psycopg2)
USER root
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy (backend.py) into the container
COPY backend/backend.py /app/backend.py

# Expose the port 
EXPOSE 8000

# Command to run FastAPI with Uvicorn
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
