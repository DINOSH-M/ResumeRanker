# AI Resume Ranker Platform

A production-ready microservices architecture for ranking resumes against job descriptions using AI and LLM analysis.

## Architecture Overview

The platform consists of the following microservices:

1. **Eureka Discovery Server** (Port 8761) - Service discovery and registration
2. **API Gateway** (Port 8080) - Single entry point with JWT authentication
3. **Auth Service** (Port 8081) - User authentication and JWT token management
4. **Resume Ranker Service** (Port 8000) - Python/FastAPI service for AI-powered resume ranking
5. **Resume Client Service** (Port 8082) - Spring Boot service that calls the Python ranker service
6. **PostgreSQL Database** - User data storage

## Prerequisites

- Docker and Docker Compose
- GEMINI_API_KEY (for LLM analysis)
- Java 17+ (for local development)
- Python 3.11+ (for local development)
- Maven 3.9+ (for local development)

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your-gemini-api-key-here
JWT_SECRET=your-secret-key-for-jwt-token-generation-min-32-chars
DB_NAME=resumeranker
DB_USER=postgres
DB_PASSWORD=postgres
```

### 2. Build and Start All Services

```bash
docker-compose up --build
```

### 3. Access Services

- **Eureka Dashboard**: http://localhost:8761
- **API Gateway**: http://localhost:8080
- **Auth Service**: http://localhost:8081
- **Resume Client Service**: http://localhost:8082
- **Resume Ranker Service**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (FastAPI Swagger UI)

## API Usage

### 1. Register a New User

```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "email": "john@example.com",
  "role": "USER"
}
```

### 3. Rank a Resume

```bash
curl -X POST http://localhost:8080/resume/rank \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=@/path/to/job_description.pdf"
```

Response:
```json
{
  "similarityScore": 0.85,
  "llmAnalysis": "HR-style analysis of the resume..."
}
```

## Service Details

### Resume Ranker Service (Python/FastAPI)

- **Technology**: Python 3.11, FastAPI, SentenceTransformer, Gemini LLM
- **Features**:
  - PDF text extraction
  - Embedding generation using "all-MiniLM-L6-v2" model
  - Cosine similarity calculation
  - LLM analysis using Gemini 1.5 Flash
- **Modules**:
  - `logic/extract_text.py` - PDF text extraction
  - `logic/embedder.py` - Sentence embedding generation
  - `logic/similarity.py` - Cosine similarity calculation
  - `logic/llm_analyzer.py` - Gemini LLM integration

### Auth Service (Spring Boot)

- **Technology**: Spring Boot 3.1.5, Java 17, PostgreSQL, JWT
- **Features**:
  - User registration and login
  - JWT token generation and validation
  - Password hashing with BCrypt
  - Role-based access control

### Resume Client Service (Spring Boot)

- **Technology**: Spring Boot 3.1.5, WebClient, Eureka Client
- **Features**:
  - JWT validation via Auth Service
  - WebClient integration with Python service
  - Multipart file handling

### API Gateway (Spring Cloud Gateway)

- **Technology**: Spring Cloud Gateway, Eureka Client
- **Features**:
  - Route configuration
  - Global JWT authentication filter
  - CORS configuration
  - Service discovery integration

### Eureka Discovery Server

- **Technology**: Spring Cloud Netflix Eureka
- **Features**:
  - Service registration and discovery
  - Health monitoring

## Development

### Running Services Locally

Each service can be run locally for development:

#### Python Service
```bash
cd resume-ranker-service
pip install -r requirements.txt
export GEMINI_API_KEY=your-key
uvicorn main:app --reload
```

#### Spring Boot Services
```bash
cd <service-name>
mvn spring-boot:run
```

## Troubleshooting

1. **Services not connecting to Eureka**: Ensure Eureka server is healthy before starting other services
2. **Database connection errors**: Check PostgreSQL is running and credentials are correct
3. **JWT validation failures**: Ensure `JWT_SECRET` is the same across auth-service and api-gateway
4. **Gemini API errors**: Verify `GEMINI_API_KEY` is set correctly

## Production Considerations

- Use environment variables for all secrets
- Implement proper logging and monitoring
- Add rate limiting
- Use HTTPS/TLS
- Implement database migrations
- Add comprehensive error handling
- Set up health checks and circuit breakers
- Use container orchestration (Kubernetes) for scaling

## License

MIT

