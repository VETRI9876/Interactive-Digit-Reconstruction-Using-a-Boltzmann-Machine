# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Set the Python path
ENV PYTHONPATH=/app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn numpy opencv-python-headless pillow jinja2 starlette python-multipart

# Expose the application port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
