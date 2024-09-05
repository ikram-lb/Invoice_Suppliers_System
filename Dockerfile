# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create and set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Create a virtual environment
RUN python -m venv /env

# Activate the virtual environment and upgrade pip
ENV PATH="/env/bin:$PATH"

RUN python -m pip install --upgrade pip

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Ensure entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Expose the necessary port
EXPOSE 8000
