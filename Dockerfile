# Base Image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage cache
COPY logsense_ai/requirements.txt .

# Install dependencies
# Upgrade pip and install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose Streamlit port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "logsense_ai/src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
