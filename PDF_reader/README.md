# PDF Teacher RAG Assistant – Portfolio Demo

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python)
![AI](https://img.shields.io/badge/AI-Intelligent%20Assistant-orange?style=flat&logo=artificial-intelligence)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-success?style=flat&logo=python)
![Offline](https://img.shields.io/badge/Offline-Fully%20Local-yellow?style=flat)
![LLM](https://img.shields.io/badge/LLM-Ollama-purple?style=flat&logo=openai)

---

## Executive Summary

The **PDF Teacher RAG Assistant** is a professional-grade, offline-capable AI application designed to read and understand PDF documents and answer natural language questions. It combines local embedding models, a Tkinter GUI, and streaming LLM responses via Ollama to create an intelligent assistant that can serve educational, research, or professional purposes. Recruiters and non-technical clients can immediately appreciate the tool’s polished interface, offline functionality, and intelligent question-answering capabilities, making it an impressive showcase project for AI and Python expertise.

---

## Future Enhancements & Knowledge Base

The PDF Teacher RAG Assistant is designed with scalability and continuous learning in mind:

- **Universal PDF Support:** Future versions could automatically handle any PDF document, including scanned PDFs via OCR, to answer questions from a wider range of sources.
- **Self-Growing Knowledge Base:** Every time a question is asked and answered correctly, the assistant can store that Q&A pair locally, continuously training its embeddings and improving semantic retrieval.
- **Offline LLM Training Integration:** By combining local embeddings with LLM feedback, the system could incrementally refine its knowledge without needing an internet connection.
- **Advanced Search & Analytics:** Users could query across multiple PDFs, track answer history, and visualize knowledge coverage.
- **Portfolio & Enterprise Ready:** These features demonstrate a forward-looking, production-grade AI application for recruiters and clients, showcasing Python, AI, and offline LLM capabilities.

This roadmap highlights the project’s potential to evolve from a PDF Q&A tool into a fully autonomous, learning knowledge assistant.

---

## Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)** workflow:

- Load PDF files and automatically segment their content into meaningful text chunks.
- Generate embeddings locally using a compact, efficient sentence-transformer model.
- Store these embeddings for fast, offline semantic search.
- Accept user questions via a clean, dark-themed Tkinter GUI.
- Retrieve contextually relevant PDF content and feed it to an LLM (Ollama) for real-time, streaming answers.
- Display the results in a professional, scrollable chat interface.

The system is designed to be **fully offline**, except for the Ollama API, providing high performance, privacy, and reliability.

---

## Features

- **Offline-friendly embeddings** using `SentenceTransformer` – no internet required for processing PDFs.
- **Tkinter GUI** with dark theme, chat display, multi-line input, and progress bars.
- **Dynamic chunking** of PDF content with configurable chunk size and overlap.
- **Streaming LLM answers** from Ollama, providing responsive, real-time feedback.
- **NumPy-based cosine similarity** for fast, offline semantic search.
- **Thread-safe UI updates** with progress bars for PDF loading and embedding generation.
- **Professional portfolio-ready design**, highlighting Python, AI, GUI, offline capabilities, and LLM integration.

---

## Screenshots

<img width="681" height="708" alt="PDF Teacher Assistant Screenshot" src="https://github.com/user-attachments/assets/71ba76fe-9a46-48e2-b13e-8aa87ae232b7" />

---

## Usage

1. Launch `teacher.py` in your Python environment.
2. Click **Load PDFs** and select the documents you want to process.
3. Ask questions in the chat input and receive streaming responses from the LLM.
4. Progress bars indicate loading and embedding generation in real-time.
5. Configure **chunk size** and **overlap** to optimize semantic retrieval for larger documents.

---

## License

This project is for portfolio demonstration purposes. Redistribution or public deployment without permission is prohibited.

