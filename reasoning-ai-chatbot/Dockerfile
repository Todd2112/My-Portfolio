# Start from the Ollama base image
FROM ollama/ollama

# Set working directory
WORKDIR /app

# Copy requirements.txt first for layer caching
COPY requirements.txt /app/requirements.txt

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r /app/requirements.txt

# Copy rest of app
COPY . /app

# Expose ports for Ollama and Streamlit
EXPOSE 11434 8501

# Start Ollama and preload model, then run Streamlit
CMD ["sh", "-c", "ollama serve & sleep 3 && ollama pull deepseek-r1:1.5b && streamlit run Python-Coder.py --server.port=8501 --server.address=0.0.0.0"]
