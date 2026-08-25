# Aurevia AI API Contract

Base URL: `/api/v1`

## Health Check
- **Endpoint**: `GET /health`
- **Description**: Returns the health status of the AI service.
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "Aurevia AI Service",
    "version": "0.1.0",
    "timestamp": "2024-05-18T12:00:00.000Z"
  }
  ```

*(To be expanded in future phases for NLP, Audio, ML, Risk, and RAG endpoints)*
