# Base image — slim keeps it small
FROM python:3.10-slim

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
COPY data/chromadb/ ./data/chromadb/

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose Streamlit's default port
EXPOSE 8501

# Use startup script instead of directly running streamlit
CMD ["./start.sh"]

