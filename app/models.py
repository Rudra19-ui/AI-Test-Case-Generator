from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import re
import json
from datetime import datetime

class Requirement(BaseModel):
    """Model for a single requirement."""
    req_id: Optional[str] = None
    text: str
    
    @validator('req_id')
    def validate_req_id(cls, v):
        """Validate requirement ID format if present."""
        if v is not None:
            if not re.match(r'^[A-Za-z0-9_-]+$', v):
                raise ValueError('Requirement ID must contain only alphanumeric characters, underscores, and hyphens')
        return v

class TestStep(BaseModel):
    """Model for a single test step."""
    step_number: int
    description: str
    expected_result: str

class TestCase(BaseModel):
    """Model for a generated test case."""
    test_id: str = Field(..., description="Unique identifier for the test case")
    title: str = Field(..., description="Short descriptive title for the test case")
    description: str = Field(..., description="Detailed description of what the test case verifies")
    preconditions: List[str] = Field(default_factory=list, description="List of preconditions required for the test")
    test_steps: List[TestStep] = Field(..., description="Ordered list of test steps")
    expected_outcome: str = Field(..., description="Overall expected outcome of the test case")
    priority: str = Field(..., description="Priority level (High, Medium, Low)")
    requirement_id: Optional[str] = Field(None, description="ID of the source requirement")
    compliance_tags: List[str] = Field(default_factory=list, description="Relevant compliance tags (HIPAA, FHIR, etc.)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority is one of the allowed values."""
        allowed = ["High", "Medium", "Low", "high", "medium", "low"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of: {', '.join(allowed)}")
        return v.capitalize()  # Normalize to capitalized form
    
    @validator('test_id')
    def validate_test_id(cls, v):
        """Validate test ID format."""
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('Test ID must contain only alphanumeric characters, underscores, and hyphens')
        return v

class GenerateRequest(BaseModel):
    """Request model for test case generation from text."""
    text: str

class TestCaseResponse(BaseModel):
    """Response model for test case generation."""
    test_cases: List[TestCase]
    count: int
    source_requirements: List[Requirement]

class ComplianceSnippet(BaseModel):
    """Model for compliance reference snippets."""
    tag: str
    text: str
    source: str
    relevance: Optional[float] = None

class JiraExportRequest(BaseModel):
    """Request model for exporting test cases to Jira."""
    test_cases: List[TestCase]
    project_key: str
    issue_type: str = "Test"