# Use the official Python image with Python 3.11
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install manually all the missing libraries
RUN apt-get update && apt-get install -y gcc python3-dev libffi-dev cron

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the container at /app
COPY . /app


# Copy the cron job file into the container at /etc/cron.d/cronjob
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply cron job
RUN crontab /etc/cron.d/cronjob

# Run the command on container startup
CMD ["cron", "-f"]
