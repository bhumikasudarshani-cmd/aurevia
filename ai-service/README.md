# Aurevia AI Intelligence Service

This directory contains the AI Intelligence Layer of the Aurevia project.

## Overview
The AI service is built with Python 3.12+ and FastAPI. It provides endpoints for NLP text analysis, audio feature extraction, machine learning risk prediction, and RAG capabilities.

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup configuration:
   ```bash
   cp .env.example .env
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Testing
Run tests using pytest:
```bash
pytest tests/
```

## Docker
Build and run with Docker:
```bash
docker build -t aurevia-ai-service .
docker run -p 8000:8000 --env-file .env aurevia-ai-service
```
