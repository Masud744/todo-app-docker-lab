# Use official Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/data

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
