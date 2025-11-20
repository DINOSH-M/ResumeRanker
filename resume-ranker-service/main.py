from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from logic.extract_text import extract_text_from_pdf
from logic.embedder import Embedder
from logic.similarity import calculate_cosine_similarity
from logic.llm_analyzer import LLMAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Ranker Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
embedder = Embedder()
llm_analyzer = None


@app.on_event("startup")
async def startup_event():
    """Initialize LLM analyzer on startup."""
    global llm_analyzer
    try:
        llm_analyzer = LLMAnalyzer()
        logger.info("Resume Ranker Service started successfully")
    except Exception as e:
        logger.error(f"Error initializing LLM analyzer: {str(e)}")
        raise


class RankResponse(BaseModel):
    similarity_score: float
    llm_analysis: str


@app.post("/rank", response_model=RankResponse)
async def rank_resume(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
    """
    Rank a resume against a job description.
    
    Args:
        resume: Resume PDF file
        job_description: Job description PDF file
        
    Returns:
        RankResponse with similarity_score and llm_analysis
    """
    try:
        # Read PDF files
        resume_content = await resume.read()
        jd_content = await job_description.read()
        
        # Extract text from PDFs
        logger.info("Extracting text from PDFs...")
        resume_text = extract_text_from_pdf(resume_content)
        jd_text = extract_text_from_pdf(jd_content)
        
        if not resume_text or not jd_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF files"
            )
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        resume_embedding = embedder.embed(resume_text)
        jd_embedding = embedder.embed(jd_text)
        
        # Calculate similarity
        logger.info("Calculating similarity...")
        similarity_score = calculate_cosine_similarity(resume_embedding, jd_embedding)
        
        # Generate LLM analysis
        logger.info("Generating LLM analysis...")
        if llm_analyzer is None:
            raise HTTPException(
                status_code=500,
                detail="LLM analyzer not initialized"
            )
        
        try:
            llm_analysis = llm_analyzer.analyze_resume(resume_text, jd_text)
            logger.info(f"LLM analysis generated successfully, length: {len(llm_analysis) if llm_analysis else 0}")
        except Exception as e:
            logger.error(f"Error generating LLM analysis: {str(e)}")
            llm_analysis = f"Error generating analysis: {str(e)}"
        
        # Ensure llm_analysis is a string
        if not isinstance(llm_analysis, str):
            llm_analysis = str(llm_analysis) if llm_analysis is not None else "Analysis unavailable"
        
        logger.info("Creating response...")
        response = RankResponse(
            similarity_score=round(similarity_score, 4),
            llm_analysis=llm_analysis
        )
        logger.info("Response created successfully")
        return response
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "resume-ranker-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

