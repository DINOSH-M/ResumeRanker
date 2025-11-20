# AI Resume Ranker Platform - Complete Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Component Details](#component-details)
4. [End-to-End Flow](#end-to-end-flow)
5. [Tech Stack Breakdown](#tech-stack-breakdown)
6. [API Documentation](#api-documentation)
7. [Security Implementation](#security-implementation)
8. [Design Patterns Used](#design-patterns-used)
9. [Interview Questions](#interview-questions)
10. [Best Practices](#best-practices)
11. [Performance Considerations](#performance-considerations)

---

## Project Overview

### What is AI Resume Ranker Platform?

The AI Resume Ranker Platform is a **microservices-based application** that uses **Artificial Intelligence** to analyze and rank resumes against job descriptions. It provides:

- **Similarity Scoring**: Uses embeddings and cosine similarity to calculate match percentage
- **AI-Powered Analysis**: Uses Google Gemini LLM to provide HR-style analysis
- **Secure Authentication**: JWT-based authentication with refresh tokens
- **Scalable Architecture**: Microservices architecture with service discovery
- **Modern UI**: Streamlit-based frontend for easy interaction

### Key Features

1. User Registration and Authentication
2. PDF Resume and Job Description Upload
3. AI-Powered Resume Analysis
4. Similarity Score Calculation
5. Detailed HR-Style Analysis
6. Secure API Gateway
7. Service Discovery and Load Balancing

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Streamlit)                    │
│                         Port: 8501                              │
│                         Tech: Python, Streamlit                 │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Spring Cloud Gateway)         │
│                      Port: 8080                                  │
│                      Tech: Java, Spring Cloud Gateway           │
│                      - JWT Validation                            │
│                      - Request Routing                           │
│                      - CORS Configuration                        │
└──────┬───────────────────────────────┬──────────────────────────┘
       │                               │
       ▼                               ▼
┌──────────────────┐          ┌──────────────────────┐
│  Auth Service    │          │ Resume Client Service │
│  Port: 8081      │          │ Port: 8082            │
│  Tech: Spring    │          │ Tech: Spring WebFlux  │
│  Boot, JPA       │          │ - JWT Validation      │
│  - User Mgmt     │          │ - File Upload         │
│  - JWT Generation│          │ - Service Integration│
│  - Token Validate│          └──────────┬────────────┘
└────────┬─────────┘                     │
         │                                ▼
         │                    ┌──────────────────────┐
         │                    │ Resume Ranker Service│
         │                    │ Port: 8000           │
         │                    │ Tech: Python, FastAPI │
         │                    │ - PDF Extraction      │
         │                    │ - Embeddings          │
         │                    │ - Similarity Calc     │
         │                    │ - LLM Analysis        │
         │                    └──────────────────────┘
         │
         ▼
┌──────────────────┐          ┌──────────────────────┐
│  Eureka Server   │          │   PostgreSQL DB      │
│  Port: 8761      │          │   Port: 5432         │
│  Tech: Spring    │          │   Tech: PostgreSQL  │
│  Cloud Netflix   │          │   - User Data        │
│  - Service       │          │   - Authentication   │
│    Discovery     │          │   - JWT Tokens       │
└──────────────────┘          └──────────────────────┘
```

### Architecture Patterns

1. **Microservices Architecture**: Each service is independently deployable
2. **API Gateway Pattern**: Single entry point for all client requests
3. **Service Discovery**: Eureka for service registration and discovery
4. **Circuit Breaker Pattern**: Resilience in service communication
5. **JWT Authentication**: Stateless authentication across services

---

## Component Details

### 1. Frontend Service (Streamlit)

#### Purpose
User interface for interacting with the application.

#### Tech Stack
- **Language**: Python 3.11
- **Framework**: Streamlit 1.30.0
- **HTTP Client**: Requests 2.31.0
- **Container**: Docker

#### Key Features
- User registration and login
- PDF file upload (drag & drop)
- Real-time status updates
- Results display (similarity score + analysis)
- Session management

#### File Structure
```
frontend/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
└── README.md            # Frontend documentation
```

#### Functional Flow
1. User opens http://localhost:8501
2. User registers/logs in → Gets JWT token
3. User uploads Resume PDF and Job Description PDF
4. Frontend sends multipart request to API Gateway with JWT token
5. Receives response with similarity score and analysis
6. Displays results to user

#### Key Code Snippets

**Authentication:**
```python
def login_user(email, password):
    response = requests.post(
        f"{API_GATEWAY_URL}/auth/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        return True, data.get("token"), "Login successful!"
```

**File Upload:**
```python
def rank_resume(resume_file, job_description_file, token):
    files = {
        'resume': ('resume.pdf', resume_file, 'application/pdf'),
        'job_description': ('job_description.pdf', job_description_file, 'application/pdf')
    }
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f"{API_GATEWAY_URL}/resume/rank",
        files=files,
        headers=headers,
        timeout=60
    )
```

---

### 2. API Gateway (Spring Cloud Gateway)

#### Purpose
Single entry point for all client requests, handles routing, authentication, and CORS.

#### Tech Stack
- **Language**: Java 17
- **Framework**: Spring Boot 3.1.5
- **Gateway**: Spring Cloud Gateway
- **Service Discovery**: Netflix Eureka Client
- **Reactive**: Spring WebFlux
- **Container**: Docker

#### Key Features
- JWT token validation
- Request routing to appropriate services
- CORS configuration
- Global error handling
- Request/Response logging

#### File Structure
```
api-gateway/
├── src/main/java/com/resumeranker/apigateway/
│   ├── ApiGatewayApplication.java
│   ├── filter/
│   │   └── JwtAuthenticationFilter.java  # Global JWT filter
│   └── dto/
│       └── TokenValidationResponse.java
├── src/main/resources/
│   └── application.yml                    # Routing configuration
├── pom.xml
└── Dockerfile
```

#### Routing Configuration

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: auth-service
          uri: lb://auth-service
          predicates:
            - Path=/auth/**
          filters:
            - StripPrefix=0
        - id: resume-client-service
          uri: lb://resume-client-service
          predicates:
            - Path=/resume/**
          filters:
            - StripPrefix=0
```

#### JWT Authentication Filter

**Flow:**
1. Intercepts all requests (except excluded paths)
2. Extracts JWT token from Authorization header
3. Validates token with Auth Service
4. Adds user info to request headers
5. Forwards request to downstream service

**Key Code:**
```java
@Component
public class JwtAuthenticationFilter implements GlobalFilter, Ordered {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // Extract token
        String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
        String token = authHeader.substring(7);
        
        // Validate with Auth Service
        return webClient.post()
            .uri("/auth/validate")
            .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
            .retrieve()
            .bodyToMono(TokenValidationResponse.class)
            .flatMap(validationResponse -> {
                if (!validationResponse.isValid()) {
                    return onError(exchange, "Invalid token", HttpStatus.UNAUTHORIZED);
                }
                // Forward request
                return chain.filter(exchange);
            });
    }
}
```

---

### 3. Authentication Service

#### Purpose
Handles user registration, login, JWT token generation, and token validation.

#### Tech Stack
- **Language**: Java 17
- **Framework**: Spring Boot 3.1.5
- **Security**: Spring Security
- **Database**: PostgreSQL
- **ORM**: Spring Data JPA
- **Password Hashing**: BCrypt
- **JWT**: JJWT library
- **Service Discovery**: Netflix Eureka Client
- **Container**: Docker

#### Key Features
- User registration with email validation
- Secure password hashing (BCrypt)
- JWT token generation (HS256)
- Refresh token mechanism
- Token validation endpoint
- Role-based access (future enhancement)

#### File Structure
```
auth-service/
├── src/main/java/com/resumeranker/auth/
│   ├── AuthServiceApplication.java
│   ├── controller/
│   │   └── AuthController.java
│   ├── service/
│   │   ├── AuthService.java
│   │   └── CustomUserDetailsService.java
│   ├── repository/
│   │   └── UserRepository.java
│   ├── model/
│   │   └── User.java
│   ├── dto/
│   │   ├── RegisterRequest.java
│   │   ├── LoginRequest.java
│   │   ├── AuthResponse.java
│   │   └── TokenValidationResponse.java
│   ├── util/
│   │   └── JwtUtil.java
│   ├── config/
│   │   └── SecurityConfig.java
│   ├── filter/
│   │   └── JwtFilter.java
│   └── exception/
│       └── GlobalExceptionHandler.java
├── src/main/resources/
│   └── application.yml
├── pom.xml
└── Dockerfile
```

#### Database Schema

**User Table:**
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Key Endpoints

**POST /auth/register**
- Request: `{ "name": "John", "email": "john@example.com", "password": "password123" }`
- Response: `{ "token": "eyJhbGci...", "refreshToken": "...", "email": "john@example.com" }`

**POST /auth/login**
- Request: `{ "email": "john@example.com", "password": "password123" }`
- Response: `{ "token": "eyJhbGci...", "refreshToken": "...", "email": "john@example.com" }`

**POST /auth/validate**
- Request: Header: `Authorization: Bearer <token>`
- Response: `{ "valid": true, "username": "john@example.com", "role": "USER" }`

#### JWT Token Structure

```json
{
  "sub": "john@example.com",
  "role": "USER",
  "iat": 1234567890,
  "exp": 1234654290
}
```

**JWT Generation:**
```java
public String generateToken(String email, String role) {
    Map<String, Object> claims = new HashMap<>();
    claims.put("role", role);
    return Jwts.builder()
        .setClaims(claims)
        .setSubject(email)
        .setIssuedAt(new Date(System.currentTimeMillis()))
        .setExpiration(new Date(System.currentTimeMillis() + jwtExpiration))
        .signWith(SignatureAlgorithm.HS256, jwtSecret)
        .compact();
}
```

**Password Hashing:**
```java
// Registration
String hashedPassword = BCrypt.hashpw(password, BCrypt.gensalt());

// Login
boolean matches = BCrypt.checkpw(password, user.getPassword());
```

---

### 4. Resume Client Service

#### Purpose
Acts as an intermediary between API Gateway and Resume Ranker Service, handles file uploads and JWT validation.

#### Tech Stack
- **Language**: Java 17
- **Framework**: Spring Boot 3.1.5
- **Reactive**: Spring WebFlux (Reactive)
- **HTTP Client**: WebClient (Reactive)
- **Service Discovery**: Netflix Eureka Client
- **Container**: Docker

#### Key Features
- Multipart file upload handling
- JWT token validation (calls Auth Service)
- File forwarding to Resume Ranker Service
- Reactive programming (non-blocking)
- Error handling and logging

#### File Structure
```
resume-client-service/
├── src/main/java/com/resumeranker/resumeclient/
│   ├── ResumeClientServiceApplication.java
│   ├── controller/
│   │   └── ResumeController.java
│   ├── service/
│   │   ├── ResumeRankerService.java      # Calls Python service
│   │   └── AuthValidationService.java    # Validates JWT
│   ├── dto/
│   │   ├── RankResponse.java
│   │   └── TokenValidationResponse.java
│   └── config/
│       └── SecurityConfig.java
├── src/main/resources/
│   └── application.yml
├── pom.xml
└── Dockerfile
```

#### Key Endpoints

**POST /resume/rank**
- Request: 
  - Header: `Authorization: Bearer <token>`
  - Multipart: `resume` (PDF file), `job_description` (PDF file)
- Response: `{ "similarity_score": 0.85, "llm_analysis": "..." }`

#### File Upload Flow

```java
public Mono<RankResponse> rankResume(FilePart resume, FilePart jobDescription) {
    return Mono.zip(
        readFilePart(resume),      // Read resume bytes
        readFilePart(jobDescription) // Read JD bytes
    ).flatMap(tuple -> {
        byte[] resumeBytes = tuple.getT1();
        byte[] jdBytes = tuple.getT2();
        
        // Create multipart form data
        MultiValueMap<String, Object> parts = new LinkedMultiValueMap<>();
        parts.add("resume", new ByteArrayResource(resumeBytes));
        parts.add("job_description", new ByteArrayResource(jdBytes));
        
        // Call Python service
        return webClient.post()
            .uri("/rank")
            .contentType(MediaType.MULTIPART_FORM_DATA)
            .body(BodyInserters.fromMultipartData(parts))
            .retrieve()
            .bodyToMono(RankResponse.class);
    });
}
```

---

### 5. Resume Ranker Service (Python/FastAPI)

#### Purpose
Core AI service that performs PDF text extraction, generates embeddings, calculates similarity, and generates LLM analysis.

#### Tech Stack
- **Language**: Python 3.11
- **Framework**: FastAPI 0.104.1
- **ASGI Server**: Uvicorn
- **PDF Processing**: PyPDF2 3.0.1
- **ML/AI**:
  - Sentence Transformers (all-MiniLM-L6-v2)
  - scikit-learn (cosine similarity)
  - Google Gemini (gemini-1.5-flash)
- **HTTP**: python-multipart (file uploads)
- **Container**: Docker

#### Key Features
- PDF text extraction
- Local embedding generation (Sentence Transformers)
- Cosine similarity calculation
- LLM-powered HR analysis (Gemini)
- Error handling and logging

#### File Structure
```
resume-ranker-service/
├── main.py                    # FastAPI application
├── logic/
│   ├── __init__.py
│   ├── extract_text.py        # PDF text extraction
│   ├── embedder.py            # Embedding generation
│   ├── similarity.py          # Cosine similarity
│   └── llm_analyzer.py       # Gemini LLM integration
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

#### Key Endpoints

**POST /rank**
- Request: Multipart form data
  - `resume`: PDF file
  - `job_description`: PDF file
- Response: 
  ```json
  {
    "similarity_score": 0.85,
    "llm_analysis": "Overall Match: 85%..."
  }
  ```

**GET /health**
- Response: `{ "status": "healthy", "service": "resume-ranker-service" }`

#### Processing Flow

```python
@app.post("/rank")
async def rank_resume(resume: UploadFile, job_description: UploadFile):
    # 1. Extract text from PDFs
    resume_text = extract_text_from_pdf(await resume.read())
    jd_text = extract_text_from_pdf(await job_description.read())
    
    # 2. Generate embeddings
    resume_embedding = embedder.embed(resume_text)
    jd_embedding = embedder.embed(jd_text)
    
    # 3. Calculate similarity
    similarity_score = calculate_cosine_similarity(resume_embedding, jd_embedding)
    
    # 4. Generate LLM analysis
    llm_analysis = llm_analyzer.analyze_resume(resume_text, jd_text)
    
    # 5. Return response
    return RankResponse(
        similarity_score=round(similarity_score, 4),
        llm_analysis=llm_analysis
    )
```

#### Embedding Generation

```python
class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)
```

**Model Details:**
- **Model**: all-MiniLM-L6-v2
- **Dimensions**: 384
- **Type**: Sentence Transformer
- **Use Case**: Semantic similarity

#### Cosine Similarity Calculation

```python
def calculate_cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Reshape for sklearn
    emb1 = embedding1.reshape(1, -1)
    emb2 = embedding2.reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(emb1, emb2)[0][0]
    
    # Ensure value is between 0 and 1
    return float(max(0.0, min(1.0, similarity)))
```

**Formula:**
```
cosine_similarity = (A · B) / (||A|| × ||B||)
```

#### LLM Analysis (Gemini)

```python
class LLMAnalyzer:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def analyze_resume(self, resume_text: str, job_description: str) -> str:
        prompt = f"""As an HR professional, analyze the following resume against the job description.
        
Job Description:
{job_description}

Resume:
{resume_text}

Please provide a comprehensive HR-style analysis including:
1. Overall match assessment
2. Key strengths
3. Potential gaps or concerns
4. Recommendations
"""
        response = self.model.generate_content(prompt)
        return response.text
```

---

### 6. Eureka Server (Service Discovery)

#### Purpose
Service registry and discovery for microservices.

#### Tech Stack
- **Language**: Java 17
- **Framework**: Spring Boot 3.1.5
- **Service Discovery**: Netflix Eureka Server
- **Container**: Docker

#### Key Features
- Service registration
- Service discovery
- Health monitoring
- Load balancing support

#### Configuration

```yaml
server:
  port: 8761

eureka:
  client:
    register-with-eureka: false
    fetch-registry: false
  server:
    enable-self-preservation: false
```

#### Access
- **Dashboard**: http://localhost:8761
- View all registered services
- Monitor service health
- Service instances

---

### 7. PostgreSQL Database

#### Purpose
Stores user data, authentication information.

#### Tech Stack
- **Database**: PostgreSQL 15-alpine
- **Container**: Docker

#### Schema

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Connection Details
- **Host**: postgres (Docker service name)
- **Port**: 5432
- **Database**: resumeranker
- **Username**: postgres
- **Password**: postgres (configurable)

---

## End-to-End Flow

### Complete Request Flow

```
1. User Action
   └─> User opens http://localhost:8501
       └─> Streamlit frontend loads

2. Authentication
   └─> User clicks "Register" or "Login"
       └─> Frontend sends POST /auth/register or /auth/login
           └─> API Gateway routes to Auth Service
               └─> Auth Service:
                   ├─> Validates input
                   ├─> Hashes password (BCrypt)
                   ├─> Saves to PostgreSQL
                   ├─> Generates JWT token
                   └─> Returns token to Frontend
                       └─> Frontend stores token in session

3. File Upload
   └─> User uploads Resume PDF and Job Description PDF
       └─> Frontend validates files (PDF format, size)

4. Resume Ranking Request
   └─> User clicks "Rank Resume"
       └─> Frontend sends POST /resume/rank
           ├─> Header: Authorization: Bearer <token>
           └─> Multipart: resume (PDF), job_description (PDF)
               └─> API Gateway:
                   ├─> JwtAuthenticationFilter intercepts
                   ├─> Extracts token from header
                   ├─> Validates token with Auth Service
                   ├─> If valid, forwards to Resume Client Service
                   └─> If invalid, returns 401 Unauthorized
                       └─> Resume Client Service:
                           ├─> Validates token again (optional double-check)
                           ├─> Reads file parts (reactive)
                           ├─> Converts to byte arrays
                           ├─> Creates multipart form data
                           └─> Calls Resume Ranker Service
                               └─> POST http://resume-ranker-service:8000/rank
                                   └─> Resume Ranker Service:
                                       ├─> Receives multipart files
                                       ├─> Extracts text from PDFs (PyPDF2)
                                       ├─> Generates embeddings (Sentence Transformers)
                                       ├─> Calculates cosine similarity
                                       ├─> Calls Gemini LLM for analysis
                                       └─> Returns JSON response
                                           {
                                             "similarity_score": 0.85,
                                             "llm_analysis": "..."
                                           }
                                           └─> Response flows back through chain
                                               └─> Frontend displays results
```

### Data Flow Diagram

```
┌─────────┐
│  User   │
└────┬────┘
     │
     ▼
┌─────────────────┐
│  Frontend       │  (Streamlit)
│  - Upload PDFs  │
│  - Display      │
└────┬────────────┘
     │ POST /resume/rank
     │ Authorization: Bearer <token>
     │ Multipart: resume, job_description
     ▼
┌─────────────────┐
│  API Gateway    │  (Spring Cloud Gateway)
│  - JWT Validate │
│  - Route        │
└────┬────────────┘
     │
     ├─────────────┐
     │             │
     ▼             ▼
┌─────────┐   ┌──────────────────┐
│  Auth   │   │ Resume Client    │
│ Service │   │ Service          │
│ Validate│   │ - File Handling  │
└─────────┘   └────┬─────────────┘
                   │ POST /rank
                   │ Multipart
                   ▼
          ┌──────────────────┐
          │ Resume Ranker    │
          │ Service          │
          │ - PDF Extract    │
          │ - Embeddings     │
          │ - Similarity     │
          │ - LLM Analysis   │
          └──────────────────┘
```

---

## Tech Stack Breakdown

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11 | Core language |
| Framework | Streamlit | 1.30.0 | Web UI framework |
| HTTP Client | Requests | 2.31.0 | API communication |
| Container | Docker | Latest | Containerization |

### API Gateway
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Java | 17 | Core language |
| Framework | Spring Boot | 3.1.5 | Application framework |
| Gateway | Spring Cloud Gateway | 2022.0.4 | API Gateway |
| Reactive | Spring WebFlux | - | Non-blocking I/O |
| Discovery | Netflix Eureka Client | - | Service discovery |
| Container | Docker | Latest | Containerization |

### Authentication Service
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Java | 17 | Core language |
| Framework | Spring Boot | 3.1.5 | Application framework |
| Security | Spring Security | - | Authentication/Authorization |
| Database | PostgreSQL | 15 | Data persistence |
| ORM | Spring Data JPA | - | Database abstraction |
| Password | BCrypt | - | Password hashing |
| JWT | JJWT | - | Token generation |
| Discovery | Netflix Eureka Client | - | Service discovery |
| Container | Docker | Latest | Containerization |

### Resume Client Service
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Java | 17 | Core language |
| Framework | Spring Boot | 3.1.5 | Application framework |
| Reactive | Spring WebFlux | - | Non-blocking I/O |
| HTTP Client | WebClient | - | Reactive HTTP client |
| Discovery | Netflix Eureka Client | - | Service discovery |
| Container | Docker | Latest | Containerization |

### Resume Ranker Service
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11 | Core language |
| Framework | FastAPI | 0.104.1 | Web framework |
| ASGI Server | Uvicorn | 0.24.0 | ASGI server |
| PDF Processing | PyPDF2 | 3.0.1 | PDF text extraction |
| ML Model | Sentence Transformers | 2.5.0+ | Embedding generation |
| Similarity | scikit-learn | 1.3.2 | Cosine similarity |
| LLM | Google Gemini | 0.3.2 | AI analysis |
| Multipart | python-multipart | 0.0.6 | File uploads |
| Container | Docker | Latest | Containerization |

### Service Discovery
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Java | 17 | Core language |
| Framework | Spring Boot | 3.1.5 | Application framework |
| Discovery | Netflix Eureka Server | - | Service registry |
| Container | Docker | Latest | Containerization |

### Database
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Database | PostgreSQL | 15-alpine | Data persistence |
| Container | Docker | Latest | Containerization |

---

## API Documentation

### Authentication Endpoints

#### POST /auth/register
**Description**: Register a new user

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiJ9...",
  "email": "john@example.com"
}
```

**Error Responses:**
- 400: Bad Request (validation error)
- 409: Conflict (email already exists)

#### POST /auth/login
**Description**: Login user and get JWT token

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiJ9...",
  "email": "john@example.com"
}
```

**Error Responses:**
- 401: Unauthorized (invalid credentials)

#### POST /auth/validate
**Description**: Validate JWT token

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "valid": true,
  "username": "john@example.com",
  "role": "USER"
}
```

**Error Responses:**
- 401: Unauthorized (invalid/expired token)

### Resume Ranking Endpoints

#### POST /resume/rank
**Description**: Rank resume against job description

**Request Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
- `resume`: PDF file
- `job_description`: PDF file

**Response (200 OK):**
```json
{
  "similarity_score": 0.85,
  "llm_analysis": "Overall Match: 85%...\n\nKey Strengths:\n- Strong experience in..."
}
```

**Error Responses:**
- 401: Unauthorized (missing/invalid token)
- 400: Bad Request (invalid files)
- 500: Internal Server Error (processing error)

---

## Security Implementation

### 1. JWT Authentication

**Token Structure:**
```json
{
  "sub": "user@example.com",
  "role": "USER",
  "iat": 1234567890,
  "exp": 1234654290
}
```

**Token Generation:**
- Algorithm: HS256
- Secret: Configurable (JWT_SECRET)
- Expiration: 24 hours (configurable)

**Token Validation:**
- API Gateway validates on every protected request
- Auth Service provides validation endpoint
- Token signature verification
- Expiration check

### 2. Password Security

**Hashing:**
- Algorithm: BCrypt
- Salt: Auto-generated
- Rounds: 10 (default)

**Best Practices:**
- Passwords never stored in plain text
- One-way hashing (cannot be reversed)
- Salt prevents rainbow table attacks

### 3. API Security

**CORS Configuration:**
- Allowed origins: * (configurable)
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed headers: *

**Request Validation:**
- Input validation on all endpoints
- File type validation (PDF only)
- File size limits

### 4. Service-to-Service Communication

**Internal Network:**
- Services communicate via Docker network
- No external exposure except API Gateway
- Service discovery via Eureka

---

## Design Patterns Used

### 1. Microservices Architecture
- **Purpose**: Scalability, independent deployment
- **Implementation**: Each service is a separate application

### 2. API Gateway Pattern
- **Purpose**: Single entry point, centralized authentication
- **Implementation**: Spring Cloud Gateway

### 3. Service Discovery Pattern
- **Purpose**: Dynamic service location
- **Implementation**: Netflix Eureka

### 4. Circuit Breaker Pattern
- **Purpose**: Fault tolerance
- **Implementation**: Spring Cloud Circuit Breaker (future)

### 5. Repository Pattern
- **Purpose**: Data access abstraction
- **Implementation**: Spring Data JPA

### 6. DTO Pattern
- **Purpose**: Data transfer between layers
- **Implementation**: Request/Response DTOs

### 7. Filter Pattern
- **Purpose**: Cross-cutting concerns (authentication)
- **Implementation**: JWT Authentication Filter

### 8. Reactive Programming
- **Purpose**: Non-blocking I/O
- **Implementation**: Spring WebFlux, Mono/Flux

---

## Interview Questions

### Architecture Questions

#### Q1: Why did you choose microservices architecture?
**Answer:**
- **Scalability**: Each service can scale independently based on load
- **Technology Diversity**: Different services can use different tech stacks (Java for backend, Python for AI)
- **Independent Deployment**: Services can be deployed without affecting others
- **Fault Isolation**: Failure in one service doesn't bring down entire system
- **Team Autonomy**: Different teams can work on different services

#### Q2: How does service discovery work in your application?
**Answer:**
- **Eureka Server**: Central registry where all services register themselves
- **Service Registration**: Each service registers with Eureka on startup
- **Service Discovery**: Services query Eureka to find other services
- **Load Balancing**: Eureka provides multiple instances for load balancing
- **Health Checks**: Eureka monitors service health and removes unhealthy instances

#### Q3: Explain the API Gateway pattern and its benefits.
**Answer:**
- **Single Entry Point**: All client requests go through API Gateway
- **Centralized Authentication**: JWT validation happens at gateway level
- **Request Routing**: Routes requests to appropriate microservices
- **CORS Handling**: Centralized CORS configuration
- **Rate Limiting**: Can implement rate limiting (future)
- **Request/Response Transformation**: Can modify requests/responses

#### Q4: How do you handle service-to-service communication?
**Answer:**
- **Synchronous**: REST APIs using WebClient (reactive) or RestTemplate
- **Service Discovery**: Use Eureka to find service instances
- **Load Balancing**: Eureka provides load balancing
- **Error Handling**: Try-catch, circuit breakers (future)
- **Timeout Configuration**: Set timeouts for service calls

### Security Questions

#### Q5: Explain JWT authentication flow in your application.
**Answer:**
1. **User Login**: User sends credentials to Auth Service
2. **Token Generation**: Auth Service validates credentials and generates JWT
3. **Token Storage**: Frontend stores token (session/memory)
4. **Request with Token**: Frontend sends token in Authorization header
5. **Token Validation**: API Gateway validates token with Auth Service
6. **Request Forwarding**: If valid, request forwarded to downstream service
7. **Token Expiration**: Token expires after 24 hours, user needs to re-login

#### Q6: Why use BCrypt for password hashing?
**Answer:**
- **One-way Hashing**: Cannot be reversed
- **Salt**: Each password has unique salt, prevents rainbow table attacks
- **Adaptive**: Can increase cost factor as hardware improves
- **Industry Standard**: Widely used and tested
- **Slow by Design**: Makes brute force attacks harder

#### Q7: How do you secure API endpoints?
**Answer:**
- **JWT Validation**: All protected endpoints require valid JWT
- **API Gateway Filter**: Global filter validates token before routing
- **Role-based Access**: Token contains role information (future enhancement)
- **HTTPS**: Should use HTTPS in production (not implemented in dev)
- **Input Validation**: Validate all inputs to prevent injection attacks

### Technology Questions

#### Q8: Why use Spring WebFlux instead of Spring MVC?
**Answer:**
- **Reactive Programming**: Non-blocking I/O, better for I/O-intensive operations
- **Scalability**: Can handle more concurrent requests with fewer threads
- **Backpressure**: Handles backpressure automatically
- **File Uploads**: Better for handling large file uploads asynchronously
- **Resource Efficiency**: Uses fewer resources for concurrent operations

#### Q9: Explain the embedding and similarity calculation process.
**Answer:**
1. **Text Extraction**: Extract text from PDFs using PyPDF2
2. **Embedding Generation**: Use Sentence Transformer model (all-MiniLM-L6-v2) to convert text to 384-dimensional vectors
3. **Similarity Calculation**: Use cosine similarity formula: (A · B) / (||A|| × ||B||)
4. **Result**: Returns value between 0 and 1, where 1 is perfect match

**Why Cosine Similarity?**
- Measures angle between vectors, not magnitude
- Good for text similarity (semantic similarity)
- Normalized (0 to 1 range)
- Works well with high-dimensional embeddings

#### Q10: How does the LLM integration work?
**Answer:**
- **API**: Google Gemini API (gemini-1.5-flash model)
- **Prompt Engineering**: Structured prompt asking for HR-style analysis
- **Input**: Resume text and job description text
- **Output**: Comprehensive analysis including match assessment, strengths, gaps, recommendations
- **Error Handling**: Graceful fallback if LLM fails

### Design Questions

#### Q11: How do you handle errors across microservices?
**Answer:**
- **Global Exception Handler**: Each service has global exception handler
- **Error Response Format**: Consistent error response format
- **HTTP Status Codes**: Proper status codes (400, 401, 404, 500)
- **Error Logging**: Log errors with context for debugging
- **Error Propagation**: Errors propagated through service chain
- **Future**: Circuit breaker pattern for fault tolerance

#### Q12: Explain the file upload flow.
**Answer:**
1. **Frontend**: User uploads PDF files via Streamlit
2. **API Gateway**: Receives multipart request, validates JWT
3. **Resume Client Service**: 
   - Receives FilePart objects (reactive)
   - Reads file content to byte arrays
   - Creates multipart form data
   - Forwards to Resume Ranker Service
4. **Resume Ranker Service**: 
   - Receives multipart files
   - Extracts text from PDFs
   - Processes and returns results

**Why Multipart?**
- Standard way to upload files in HTTP
- Supports multiple files in one request
- Efficient for binary data

#### Q13: How do you ensure data consistency?
**Answer:**
- **Database**: PostgreSQL for ACID compliance
- **Transactions**: Spring Data JPA handles transactions
- **Idempotency**: API endpoints are idempotent where possible
- **Validation**: Input validation at multiple layers
- **Future**: Distributed transactions (Saga pattern) if needed

### Performance Questions

#### Q14: How do you optimize performance?
**Answer:**
- **Reactive Programming**: Non-blocking I/O for better concurrency
- **Connection Pooling**: Database connection pooling
- **Caching**: Can implement caching (Redis) for frequently accessed data
- **Async Processing**: File processing is async
- **Load Balancing**: Eureka provides load balancing
- **Resource Optimization**: Docker containers with resource limits

#### Q15: How would you scale this application?
**Answer:**
- **Horizontal Scaling**: Add more instances of services
- **Load Balancing**: Eureka provides load balancing
- **Database Scaling**: Read replicas, sharding
- **Caching**: Redis for caching frequently accessed data
- **CDN**: For static assets
- **Message Queue**: For async processing (Kafka/RabbitMQ)
- **Container Orchestration**: Kubernetes for auto-scaling

### DevOps Questions

#### Q16: Explain your Docker setup.
**Answer:**
- **Multi-stage Builds**: Separate build and runtime stages
- **Docker Compose**: Orchestrates all services
- **Networks**: Services communicate via Docker network
- **Volumes**: Persistent storage for database
- **Health Checks**: Health check endpoints for each service
- **Environment Variables**: Configurable via environment variables

#### Q17: How do you handle service dependencies?
**Answer:**
- **Docker Compose**: `depends_on` for service startup order
- **Health Checks**: Wait for services to be healthy
- **Retry Logic**: Services retry connections if downstream service unavailable
- **Circuit Breaker**: Can implement circuit breaker pattern (future)

### Testing Questions

#### Q18: How would you test this application?
**Answer:**
- **Unit Tests**: Test individual components (services, utilities)
- **Integration Tests**: Test service interactions
- **API Tests**: Test API endpoints (Postman, REST Assured)
- **End-to-End Tests**: Test complete user flows
- **Load Tests**: Test under load (JMeter, Gatling)
- **Security Tests**: Test authentication, authorization

### Problem-Solving Questions

#### Q19: How did you handle the 415 Unsupported Media Type error?
**Answer:**
- **Root Cause**: Resume Client Service had both Spring MVC and WebFlux dependencies
- **Solution**: Removed Spring MVC, kept only WebFlux
- **Additional**: Added `consumes = MULTIPART_FORM_DATA_VALUE` to controller
- **Result**: Service now properly handles multipart requests

#### Q20: How did you fix the 403 Forbidden error?
**Answer:**
- **Root Cause**: Spring Security was blocking requests without authentication mechanism
- **Solution**: Changed SecurityConfig to `permitAll()` since API Gateway handles authentication
- **Rationale**: API Gateway validates JWT, no need for double authentication

#### Q21: How did you resolve the 404 Not Found error?
**Answer:**
- **Root Cause**: `spring.webflux.base-path` was conflicting with `@RequestMapping`
- **Solution**: Removed `base-path` configuration
- **Result**: Endpoints now work correctly with controller's `@RequestMapping`

---

## Best Practices

### 1. Code Organization
- **Separation of Concerns**: Each service has clear responsibility
- **Package Structure**: Organized by layers (controller, service, repository)
- **DTO Pattern**: Use DTOs for data transfer
- **Exception Handling**: Global exception handlers

### 2. Security
- **Password Hashing**: Always hash passwords (BCrypt)
- **JWT Expiration**: Set appropriate expiration times
- **Input Validation**: Validate all inputs
- **HTTPS**: Use HTTPS in production
- **Secrets Management**: Store secrets securely (environment variables, secrets manager)

### 3. Error Handling
- **Consistent Error Format**: Standard error response format
- **Proper HTTP Status Codes**: Use appropriate status codes
- **Error Logging**: Log errors with context
- **User-Friendly Messages**: Don't expose internal errors to users

### 4. Performance
- **Async Processing**: Use reactive programming for I/O operations
- **Connection Pooling**: Configure database connection pools
- **Caching**: Cache frequently accessed data
- **Resource Limits**: Set Docker resource limits

### 5. Monitoring
- **Health Checks**: Implement health check endpoints
- **Logging**: Structured logging with appropriate levels
- **Metrics**: Collect metrics (response times, error rates)
- **Tracing**: Distributed tracing for debugging

### 6. Documentation
- **API Documentation**: Document all endpoints
- **Code Comments**: Comment complex logic
- **README**: Comprehensive README with setup instructions
- **Architecture Diagrams**: Visual representation of architecture

---

## Performance Considerations

### 1. Database
- **Connection Pooling**: Configure appropriate pool size
- **Indexes**: Add indexes on frequently queried columns
- **Query Optimization**: Optimize database queries
- **Read Replicas**: Use read replicas for read-heavy workloads

### 2. API Gateway
- **Caching**: Cache responses where appropriate
- **Rate Limiting**: Implement rate limiting
- **Request Timeout**: Set appropriate timeouts
- **Connection Pooling**: Pool connections to downstream services

### 3. File Processing
- **Async Processing**: Process files asynchronously
- **Streaming**: Stream large files instead of loading into memory
- **File Size Limits**: Set appropriate file size limits
- **Cleanup**: Clean up temporary files

### 4. LLM Integration
- **Caching**: Cache LLM responses for similar inputs
- **Timeout**: Set timeout for LLM API calls
- **Retry Logic**: Implement retry with exponential backoff
- **Fallback**: Graceful fallback if LLM fails

### 5. Embeddings
- **Model Caching**: Cache loaded model
- **Batch Processing**: Process multiple texts in batch
- **GPU Acceleration**: Use GPU if available (future)

---

## Conclusion

This AI Resume Ranker Platform demonstrates:

1. **Microservices Architecture**: Scalable, maintainable architecture
2. **Modern Technologies**: Latest frameworks and tools
3. **Security**: JWT authentication, password hashing
4. **AI Integration**: Embeddings, similarity, LLM analysis
5. **Best Practices**: Error handling, logging, documentation
6. **Production-Ready**: Docker, health checks, monitoring

### Key Takeaways for Interview

- **Architecture**: Understand microservices, API Gateway, service discovery
- **Security**: JWT, password hashing, API security
- **Technology**: Spring Boot, FastAPI, Docker, PostgreSQL
- **AI/ML**: Embeddings, cosine similarity, LLM integration
- **Problem-Solving**: How you fixed various errors
- **Best Practices**: Error handling, logging, documentation

### Future Enhancements

1. **Caching**: Redis for caching
2. **Message Queue**: Kafka/RabbitMQ for async processing
3. **Monitoring**: Prometheus, Grafana
4. **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
5. **CI/CD**: Jenkins, GitLab CI, GitHub Actions
6. **Kubernetes**: Container orchestration
7. **API Versioning**: Version APIs
8. **Rate Limiting**: Implement rate limiting
9. **Circuit Breaker**: Resilience patterns
10. **Distributed Tracing**: Zipkin, Jaeger

---

**Document Version**: 1.0  
**Last Updated**: November 2024  
**Author**: AI Resume Ranker Platform Team

