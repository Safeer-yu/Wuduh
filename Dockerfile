# Base image — slim keeps it small
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first — Docker caches this layer
# so it won't reinstall packages on every build
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY src/ ./src/
COPY data/chunks/ ./data/chunks/

# Expose Streamlit's default port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]