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

---

## NLP Pipeline (Phase 2)

```
POST /api/v1/nlp/analyze
        ↓
   Validation (Pydantic schema)
        ↓
   Length check (10 000 char limit)
        ↓
   Text Preprocessing
     - Unicode NFC normalization
     - Control character removal
     - Whitespace normalization
     - Metrics (chars, words, sentences)
        ↓
   Tokenization   (SimpleTokenizer — replaceable)
        ↓
   Language Detection  (HeuristicLanguageDetector — replaceable)
        ↓
   NLP Model  (DemoNLPModel → future transformer)
        ↓
   Embedding  (DemoEmbeddingProvider → future SentenceTransformer)
        ↓
   NLPAnalyzeResponse (Pydantic)
```

### DEMO_MODE
When `DEMO_MODE=true` (default), the pipeline runs entirely with built-in
lightweight implementations — no downloads, no GPU, no API keys required.

---

## Audio Pipeline (Phase 3)

```
POST /api/v1/audio/analyze (multipart/form-data)
        ↓
   AudioFileValidator
     - Sanitises filename
     - Checks allowed extensions & MIME types
     - Size limit check (default 50MB)
     - Magic bytes verification
        ↓
   BaseObjectStorage
     - LocalObjectStorage (DEMO_MODE / default)
     - MinIOObjectStorage (Production)
        ↓
   AudioMetadataExtractor
     - Natively parses WAV RIFF headers
     - Returns placeholders for other formats in demo mode
        ↓
   AudioFeatureExtractor
     - DEMO: pure-Python byte-level statistics (RMS, ZCR, entropy)
     - PROD: lazily loads librosa/soundfile for acoustic features
        ↓
   BaseTranscriptionProvider (Stub)
     - Interface ready for Whisper / Google STT in later phases
        ↓
   AudioAnalyzeResponse (Pydantic)
```

### Security & Path Traversal
- Raw filenames from uploads are **never** used to construct internal paths.
- Paths are generated via UUIDs.
- `LocalObjectStorage` forcibly resolves paths and guarantees they do not escape the configured base directory.
