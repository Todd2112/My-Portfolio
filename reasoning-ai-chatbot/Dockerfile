# Use Ollama base image
FROM ollama/ollama

# Set working directory
WORKDIR /app

# Copy Streamlit app and requirements
COPY requirements.txt .
COPY Python-Coder.py .
COPY start.sh .

# Install Python + Streamlit dependencies
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Make start.sh executable
RUN chmod +x start.sh

# Expose necessary ports
EXPOSE 11434 8080

# Start both Ollama and Streamlit via startup script
CMD ["/app/start.sh"]
