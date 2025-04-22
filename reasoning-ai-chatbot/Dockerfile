# Base image with Ollama and Python
FROM ollama/ollama:latest

# Set working directory
WORKDIR /app

# Copy all necessary files
COPY . .

# Make the start script executable
RUN chmod +x /app/start.sh

# Expose the Streamlit default port
EXPOSE 8080

# Override Ollama's default entrypoint so we can run our script
ENTRYPOINT []

# Use our startup script as the default command
CMD ["/app/start.sh"]
