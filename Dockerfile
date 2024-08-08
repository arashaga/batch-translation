# Use the official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the ports
EXPOSE 8000
EXPOSE 80

# Command to run FastAPI on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Command to run Streamlit on port 80
# Note: This command won't be used directly, but will be useful in the docker-compose.yml
CMD ["streamlit", "run", "app.py", "--server.port=80", "--server.enableCORS=false"]
