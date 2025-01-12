# Use the official Python 3.12 image as the base image
FROM python:3.12

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install the Python dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container at /app
COPY . .

# Expose port 80 to allow external access to the container's port 80
EXPOSE 80

# Specify the command to run when the container starts
CMD ["python", "app.py"]
