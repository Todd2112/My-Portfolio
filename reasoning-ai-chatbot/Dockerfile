# Start from the Ollama base image
FROM ollama/ollama

# Set the working directory
WORKDIR /app

# Copy your app into the container
COPY . /app

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Preload the DeepSeek model (or any model you prefer)
RUN ollama pull deepseek-r1:1.5b

# Expose the ports (Ollama & Streamlit)
EXPOSE 11434 8501

# Start both Ollama and Streamlit using a script
CMD ["sh", "-c", "ollama serve & streamlit run Python-Coder.py --server.port=8501 --server.address=0.0.0.0"]
