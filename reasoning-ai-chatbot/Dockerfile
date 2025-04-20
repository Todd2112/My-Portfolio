# Start from the Ollama base image
FROM ollama/ollama

# Set environment variable to avoid interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy your app into the container
COPY . /app

# Install Python, pip, and other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Optional: preload a model (uncomment if desired)
# RUN ollama pull deepseek-coder

# Expose both Ollama and Streamlit ports
EXPOSE 11434 8501

# Start Ollama and Streamlit together
CMD ["sh", "-c", "ollama serve & streamlit run Python-Coder.py --server.port=8501 --server.address=0.0.0.0"]
