# Use Ollama base image
FROM ollama/ollama:latest

# Working directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Make sure start.sh is executable
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 8501 11434

# Prevent inherited ENTRYPOINT from Ollama
ENTRYPOINT []

# Start Streamlit and Ollama
CMD ["/app/start.sh"]
