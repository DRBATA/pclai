FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY python-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire python-backend directory
COPY python-backend/ .

# Expose port
EXPOSE 8080

# Run the app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
