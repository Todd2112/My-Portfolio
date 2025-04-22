# Base image with Python and Ollama
FROM ollama/ollama

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python and pip if not present (for minimal base images)
RUN apt-get update && apt-get install -y python3-pip

# Install Python dependencies
RUN pip install --no-cache-dir streamlit

# Make the start script executable
RUN chmod +x /app/start.sh

# Default start command
CMD ["/app/start.sh"]
