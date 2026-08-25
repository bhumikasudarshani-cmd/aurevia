# Aurevia AI Architecture

## Overview
The Aurevia AI Service is a microservice designed to support human reviewers by providing AI-assisted decision-support metrics based on textual, auditory, structured, and historical data.

## Key Technologies
- **Framework**: FastAPI (Python 3.12+)
- **ML/AI**: PyTorch, Hugging Face Transformers, Sentence Transformers, scikit-learn, XGBoost, Librosa, OpenSMILE
- **Database**: PostgreSQL (via SQLAlchemy/Alembic) with TimescaleDB and pgvector
- **Messaging**: RabbitMQ / Celery (for async tasks)
- **Storage**: MinIO / S3
- **Local LLM**: Ollama

## Modules
- `nlp/`: Processes text using Transformers.
- `audio/`: Extracts features using Librosa and OpenSMILE.
- `ml/`: Predicts risk scores using XGBoost and SHAP explainability.
- `risk/`: Calculates explainable, combined decision-support scores.
- `rag/`: Manages knowledge ingestion, embedding, and retrieval.
- `storage/`: Interfaces with PostgreSQL, pgvector, and MinIO.

*(More detailed architecture diagrams and documentation will be added as phases progress)*
