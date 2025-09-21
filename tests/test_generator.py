import pytest
import json
from unittest.mock import patch, MagicMock

from app.models import Requirement, TestCase, TestStep
from app.generator import split_requirements, generate_test_case, generate_test_cases
from app.llm_client import safe_parse_json

# Sample test data
SAMPLE_REQUIREMENT_TEXT = """
REQ-001: The system shall allow users to view patient medical history in a chronological timeline.

REQ-002: The system shall encrypt all patient data at rest using AES-256 encryption.
"""

SAMPLE_REQUIREMENT = Requirement(
    req_id="REQ-001",
    text="The system shall allow users to view patient medical history in a chronological timeline."
)

SAMPLE_TEST_CASE_JSON = """
{
  "test_id": "TC-REQ-001-001",
  "title": "Verify Patient Medical History Timeline Display",
  "description": "Verify that authorized users can view a patient's medical history in chronological order",
  "preconditions": ["User is logged in with appropriate permissions", "Patient record exists in the system"],
  "test_steps": [
    {
      "step_number": 1,
      "description": "Navigate to patient records section",
      "expected_result": "Patient records interface is displayed"
    },
    {
      "step_number": 2,
      "description": "Search for and select a specific patient",
      "expected_result": "Patient details page is displayed"
    },
    {
      "step_number": 3,
      "description": "Click on 'Medical History' tab",
      "expected_result": "Medical history is displayed in chronological order with most recent entries at the top"
    }
  ],
  "expected_outcome": "The system displays the patient's medical history in a chronological timeline format that is easy to navigate and understand",
  "priority": "High",
  "requirement_id": "REQ-001"
}
"""

@pytest.mark.asyncio
async def test_split_requirements():
    """Test splitting requirements text into Requirement objects."""
    requirements = await split_requirements(SAMPLE_REQUIREMENT_TEXT)
    
    assert len(requirements) == 2
    assert requirements[0].req_id == "REQ-001"
    assert "view patient medical history" in requirements[0].text
    assert requirements[1].req_id == "REQ-002"
    assert "encrypt all patient data" in requirements[1].text

@pytest.mark.asyncio
async def test_split_requirements_numbered_list():
    """Test splitting numbered list requirements."""
    numbered_requirements = """
    1. The system shall support single sign-on authentication.
    2. The system shall maintain an audit log of all data access.
    """
    
    requirements = await split_requirements(numbered_requirements)
    
    assert len(requirements) == 2
    assert requirements[0].req_id == "REQ-1"
    assert "single sign-on" in requirements[0].text
    assert requirements[1].req_id == "REQ-2"
    assert "audit log" in requirements[1].text

@pytest.mark.asyncio
async def test_split_requirements_paragraphs():
    """Test splitting requirements by paragraphs."""
    paragraph_requirements = """
    The system shall support role-based access control.
    
    The system shall allow administrators to define custom roles.
    """
    
    requirements = await split_requirements(paragraph_requirements)
    
    assert len(requirements) == 2
    assert requirements[0].req_id == "REQ-001"
    assert "role-based access control" in requirements[0].text
    assert requirements[1].req_id == "REQ-002"
    assert "custom roles" in requirements[1].text

def test_safe_parse_json():
    """Test JSON parsing with various formats."""
    # Standard JSON
    result = safe_parse_json(SAMPLE_TEST_CASE_JSON)
    assert result["test_id"] == "TC-REQ-001-001"
    
    # JSON with code fences
    code_fenced_json = "```json\n" + SAMPLE_TEST_CASE_JSON + "\n```"
    result = safe_parse_json(code_fenced_json)
    assert result["test_id"] == "TC-REQ-001-001"
    
    # JSON with single quotes
    single_quoted_json = SAMPLE_TEST_CASE_JSON.replace('"', "'")
    result = safe_parse_json(single_quoted_json)
    assert result["test_id"] == "TC-REQ-001-001"
    
    # JSON with trailing comma
    trailing_comma_json = SAMPLE_TEST_CASE_JSON.replace("}", "},")
    result = safe_parse_json(trailing_comma_json)
    assert result["test_id"] == "TC-REQ-001-001"

@pytest.mark.asyncio
async def test_generate_test_case():
    """Test generating a test case from a requirement."""
    # Mock the LLM client and vectorstore
    with patch("app.generator.llm_client.generate") as mock_generate, \
         patch("app.generator.vectorstore.query") as mock_query:
        
        # Setup mock responses
        mock_generate.return_value = SAMPLE_TEST_CASE_JSON
        mock_query.return_value = [
            MagicMock(id="HIPAA-1", tag="HIPAA:Audit"),
            MagicMock(id="HIPAA-Privacy", tag="HIPAA:Privacy")
        ]
        
        # Call the function
        test_case = await generate_test_case(SAMPLE_REQUIREMENT)
        
        # Verify results
        assert isinstance(test_case, TestCase)
        assert test_case.test_id == "TC-REQ-001-001"
        assert test_case.title == "Verify Patient Medical History Timeline Display"
        assert len(test_case.test_steps) == 3
        assert test_case.priority == "High"
        assert len(test_case.compliance_tags) == 2
        assert "HIPAA-Security" in test_case.compliance_tags
        assert "HIPAA-Privacy" in test_case.compliance_tags

@pytest.mark.asyncio
async def test_generate_test_cases():
    """Test generating multiple test cases from requirements text."""
    # Mock the generate_test_case function
    with patch("app.generator.generate_test_case") as mock_generate_test_case, \
         patch("app.generator.split_requirements") as mock_split_requirements:
        
        # Setup mock responses
        mock_test_case = MagicMock(spec=TestCase)
        mock_test_case.test_id = "TC-REQ-001-001"
        mock_generate_test_case.return_value = mock_test_case
        
        mock_requirements = [
            Requirement(req_id="REQ-001", text="Requirement 1"),
            Requirement(req_id="REQ-002", text="Requirement 2")
        ]
        mock_split_requirements.return_value = mock_requirements
        
        # Call the function
        test_cases, requirements = await generate_test_cases("Sample requirements text")
        
        # Verify results
        assert len(test_cases) == 2
        assert len(requirements) == 2
        assert mock_generate_test_case.call_count == 2