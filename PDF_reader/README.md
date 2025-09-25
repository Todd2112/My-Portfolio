# PDF RAG Assistant – Portfolio Demo

---

## Executive Summary

The **PDF RAG Assistant** is a professional, offline-capable AI application that reads and understands PDF documents, answering natural language questions accurately. It leverages local embedding models, a Streamlit GUI, and streaming LLM responses via Ollama to deliver an intelligent assistant suitable for educational, research, or professional environments. Its polished interface, offline functionality, and real-time question-answering make it an ideal portfolio project demonstrating Python, AI, and semantic search expertise.

---

## Future Enhancements & Knowledge Base

The PDF RAG Assistant is designed for scalability and continuous improvement:

- **Universal PDF Support:** Future versions could incorporate OCR to handle scanned PDFs, expanding the range of supported documents.
- **Self-Growing Knowledge Base:** Correctly answered Q&A pairs can be stored locally, updating embeddings and improving semantic retrieval over time.
- **Offline LLM Training Integration:** Embeddings combined with local LLM feedback could allow incremental knowledge refinement without internet access.
- **Advanced Search & Analytics:** Users could query multiple PDFs, track answer history, and visualize knowledge coverage.
- **Enterprise Ready:** These features showcase the potential for a production-grade, offline-capable AI assistant, highlighting Python, AI, and LLM integration for recruiters and clients.

This roadmap demonstrates the project’s evolution from a PDF Q&A tool to a fully autonomous, learning knowledge assistant.

---

## Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)** workflow:

- Load PDF files and segment content into meaningful text chunks automatically.
- Generate embeddings locally using a compact, efficient sentence-transformer model.
- Store embeddings for fast, offline semantic search.
- Accept user questions through a clean, professional Streamlit GUI.
- Retrieve contextually relevant PDF content and provide it to an LLM (Ollama) for real-time answers.
- Display results in a professional, scrollable chat interface.

The system is designed to operate **fully offline**, except for the Ollama API, ensuring privacy, reliability, and high performance.

---

## Features

- **Offline embeddings** using `SentenceTransformer` – process PDFs without internet access.
- **Streamlit GUI** with multi-line input, configurable settings, and chat interface.
- **Dynamic chunking** of PDF content with adjustable size and overlap for semantic accuracy.
- **Streaming LLM answers** via Ollama for responsive, real-time feedback.
- **Fast semantic search** using NumPy-based cosine similarity.
- **Portfolio-ready design** emphasizing Python, offline capabilities, GUI, and LLM integration.

---

## About the Source PDF

The application uses the book **"Artificial Intelligence and Librarianship: Notes for Teaching" (3rd Edition)** by Martin Frické. This open-source resource provides insights into AI's impact on librarianship and is licensed under a Creative Commons Attribution 4.0 International License. ([softoption.us](https://softoption.us/AIandLibrarianship?utm_source=chatgpt.com))

---

## Screenshots

**Main Interface:**

![PDF RAG Main](https://github.com/Todd2112/My-Portfolio/blob/master/PDF_reader/teacher.png)

**Sidebar & PDF Management:**

![PDF RAG Sidebar](https://github.com/Todd2112/My-Portfolio/blob/master/PDF_reader/teacher_side.png)

---

For more information and to access the source PDF, visit: [Artificial Intelligence and Librarianship](https://softoption.us/AIandLibrarianship)
