# Starts from the python 3.10 official docker image
FROM python:3.10

# Create a folder "app" at the root of the image
RUN mkdir /api

# Define /app as the working directory
WORKDIR /api

# Copy all the files in the api directory in /app
COPY . /api

# Update pip
RUN pip install --upgrade pip

# Install dependencies from "requirements.txt"
RUN pip install -r requirements.txt

# Run the app
# Set host to 0.0.0.0 to make it run on the container's network
CMD uvicorn app:app --host 0.0.0.0