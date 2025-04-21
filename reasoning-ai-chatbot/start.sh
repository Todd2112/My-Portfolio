#!/bin/bash

echo "🚀 Starting Ollama + Streamlit AI Coder App..."

# Start Ollama in the background
ollama serve &

# Optional: preload your model (can comment this out after first run)
ollama pull llama3 &

# Wait briefly to make sure Ollama is ready
sleep 10

# Start your Streamlit app
streamlit run Python-Coder.py --server.port=8080 --server.address=0.0.0.0
