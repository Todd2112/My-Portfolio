# PDF Teacher RAG Assistant – Portfolio Demo

---

## Executive Summary

The **PDF Teacher RAG Assistant** is a professional-grade, offline-capable AI application designed to read and understand PDF documents and answer natural language questions. It combines local embedding models, a Streamlit GUI, and streaming LLM responses via Ollama to create an intelligent assistant that can serve educational, research, or professional purposes. Recruiters and non-technical clients can immediately appreciate the tool’s polished interface, offline functionality, and intelligent question-answering capabilities, making it an impressive showcase project for Python and AI expertise.

---

## Future Enhancements & Knowledge Base

The PDF Teacher RAG Assistant is designed with scalability and continuous learning in mind:

- **Universal PDF Support:** Future versions could automatically handle any PDF document, including scanned PDFs via OCR, to answer questions from a wider range of sources.
- **Self-Growing Knowledge Base:** Every time a question is asked and answered correctly, the assistant can store that Q&A pair locally, continuously training its embeddings and improving semantic retrieval.
- **Offline LLM Training Integration:** By combining local embeddings with LLM feedback, the system could incrementally refine its knowledge without needing an internet connection.
- **Advanced Search & Analytics:** Users could query across multiple PDFs, track answer history, and visualize knowledge coverage.
- **Enterprise Ready:** These features demonstrate a forward-looking, production-grade AI application for recruiters and clients, showcasing Python, AI, and offline LLM capabilities.

This roadmap highlights the project’s potential to evolve from a PDF Q&A tool into a fully autonomous, learning knowledge assistant.

---

## Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)** workflow:

- Load PDF files and automatically segment their content into meaningful text chunks.
- Generate embeddings locally using a compact, efficient sentence-transformer model.
- Store these embeddings for fast, offline semantic search.
- Accept user questions via a clean, dark-themed Streamlit GUI.
- Retrieve contextually relevant PDF content and feed it to an LLM (Ollama) for real-time, streaming answers.
- Display the results in a professional, scrollable chat interface.

The system is designed to be **fully offline**, except for the Ollama API, providing high performance, privacy, and reliability.

---

## Features

- **Offline-friendly embeddings** using `SentenceTransformer` – no internet required for processing PDFs.
- **Streamlit GUI** with dark theme, chat display, multi-line input, and progress bars.
- **Dynamic chunking** of PDF content with configurable chunk size and overlap.
- **Streaming LLM answers** from Ollama, providing responsive, real-time feedback.
- **NumPy-based cosine similarity** for fast, offline semantic search.
- **Professional portfolio-ready design**, highlighting Python, GUI, offline capabilities, and LLM integration.

---

## About the Source PDF

The application utilizes the book **"Artificial Intelligence and Librarianship: Notes for Teaching" (3rd Edition)** by Martin Frické. This open-source resource provides comprehensive insights into AI's impact on librarianship and is licensed under a Creative Commons Attribution 4.0 International License. ([softoption.us](https://softoption.us/AIandLibrarianship?utm_source=chatgpt.com))

---

## Screenshots

**Main Interface:**

![PDF Teacher Main](https://github.com/Todd2112/My-Portfolio/blob/master/PDF_reader/teacher.png)

**Sidebar & PDF Management:**

![PDF Teacher Sidebar](https://github.com/Todd2112/My-Portfolio/blob/master/PDF_reader/teacher_side.png)

---

For more information and to access the source PDF, visit the official page: [Artificial Intelligence and Librarianship](https://softoption.us/AIandLibrarianship).  
