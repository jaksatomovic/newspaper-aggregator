# Use the official Python image with Python 3.11
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install manually all the missing libraries
RUN apt-get update && apt-get install -y python3-dev libffi-dev

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container at /app
COPY . /app

# Run the Python script when the container starts
CMD ["python", "main.py", ">>", "/logs/app.log", "2>&1"]

