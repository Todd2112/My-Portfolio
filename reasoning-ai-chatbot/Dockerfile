# Start from the Ollama base image
FROM ollama/ollama

# Set the working directory
WORKDIR /app

# Copy requirements.txt separately
COPY requirements.txt /app/requirements.txt

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . /app

# Preload the DeepSeek model
RUN ollama pull deepseek-r1:1.5b

# Expose the ports (Ollama & Streamlit)
EXPOSE 11434 8501

# Start both Ollama and Streamlit
CMD ["sh", "-c", "ollama serve & streamlit run Python-Coder.py --server.port=8501 --server.address=0.0.0.0"]
