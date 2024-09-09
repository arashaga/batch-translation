# Use the official Python image
FROM python:3.11

# Set the working directory
WORKDIR .

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the ports
EXPOSE 80

# Command to run FastAPI on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
