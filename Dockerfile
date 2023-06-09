# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir ccxt requests python-dotenv

# Run bot.py when the container launches, CMD args will be overridden by kubernetes job
CMD ["python", "bot.py"]
