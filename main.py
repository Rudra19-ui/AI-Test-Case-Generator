import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

from app.models import GenerateRequest, TestCaseResponse, TestCase, Requirement
from app.generator import generate_test_cases
from app.config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Test Case Generator",
    description="Generate comprehensive test cases from software requirements using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Test Case Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate": "/generate",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}

@app.post("/generate", response_model=TestCaseResponse)
async def generate_test_cases_endpoint(request: GenerateRequest):
    """Generate test cases from requirements text."""
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Requirements text cannot be empty")
        
        logger.info(f"Generating test cases for text: {request.text[:100]}...")
        
        # Generate test cases
        test_cases, requirements = await generate_test_cases(request.text)
        
        if not test_cases:
            raise HTTPException(status_code=500, detail="Failed to generate test cases")
        
        response = TestCaseResponse(
            test_cases=test_cases,
            count=len(test_cases),
            source_requirements=requirements
        )
        
        logger.info(f"Successfully generated {len(test_cases)} test cases")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/test-cases", response_model=List[TestCase])
async def list_test_cases():
    """List all generated test cases (placeholder for future implementation)."""
    return []

@app.get("/requirements", response_model=List[Requirement])
async def list_requirements():
    """List all parsed requirements (placeholder for future implementation)."""
    return []

if __name__ == "__main__":
    # Validate settings
    if not settings.validate():
        logger.warning("Some required settings are missing. The application may not work correctly.")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
