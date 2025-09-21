import json
import logging
import re
from typing import Dict, Any, Optional

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_parse_json(json_string: str) -> Dict[str, Any]:
    """Safely parse JSON string with various fallback strategies."""
    if not json_string:
        return {}
    
    # Remove code fences if present
    json_string = re.sub(r'^```json\s*', '', json_string, flags=re.MULTILINE)
    json_string = re.sub(r'\s*```$', '', json_string, flags=re.MULTILINE)
    
    # Try to parse as-is first
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        pass
    
    # Try to fix common JSON issues
    try:
        # Replace single quotes with double quotes
        fixed_json = re.sub(r"'([^']*)':", r'"\1":', json_string)
        fixed_json = re.sub(r":\s*'([^']*)'", r': "\1"', fixed_json)
        fixed_json = re.sub(r"'([^']*)'", r'"\1"', fixed_json)
        
        # Remove trailing commas
        fixed_json = re.sub(r',\s*}', '}', fixed_json)
        fixed_json = re.sub(r',\s*]', ']', fixed_json)
        
        return json.loads(fixed_json)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from mixed content
    try:
        json_match = re.search(r'\{.*\}', json_string, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    
    logger.error(f"Failed to parse JSON: {json_string[:200]}...")
    return {}

async def generate(prompt: str, max_tokens: Optional[int] = None) -> str:
    """Generate text using OpenAI API."""
    if not settings.OPENAI_API_KEY:
        logger.error("OpenAI API key not configured")
        return ""
    
    try:
        import openai
        
        response = await openai.ChatCompletion.acreate(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert test case generator for healthcare software. Generate comprehensive, detailed test cases that follow best practices for software testing."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens or settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE
        )
        
        return response.choices[0].message.content.strip()
    
    except ImportError:
        logger.error("OpenAI package not installed. Please install with: pip install openai")
        return ""
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        return ""

def create_test_case_prompt(requirement_text: str, compliance_tags: list = None) -> str:
    """Create a prompt for generating a test case from a requirement."""
    compliance_context = ""
    if compliance_tags:
        compliance_context = f"\n\nRelevant compliance requirements: {', '.join(compliance_tags)}"
    
    prompt = f"""
You are an expert QA engineer. Generate detailed test cases for each requirement separately.

Requirements: {requirement_text}

Rules:
1. Create AT LEAST 3 test cases for EACH requirement.
2. Each test case MUST have:
   - test_id (format: TC-REQ-XXX-YYY where XXX is requirement number and YYY is test case number)
   - title (clear, descriptive title)
   - description (detailed explanation of what is being tested)
   - preconditions (list of conditions that must be met before test execution)
   - test_steps (MINIMUM 3 steps per case, each with step_number, description, expected_result)
   - expected_outcome (overall expected result of the test)
   - priority (High/Medium/Low)
   - compliance_tags (e.g., HIPAA, Security, PCI if relevant) {compliance_context}
3. Do NOT merge multiple requirements into one. Each requirement should generate its own set of test cases.
4. Output must be strict JSON in this format:

{{
  "test_cases": [
    {{
      "test_id": "TC-REQ-001-001",
      "title": "Verify login with valid credentials",
      "description": "Ensures user can log in successfully",
      "preconditions": ["User exists in system"],
      "test_steps": [
        {{"step_number": 1, "description": "Navigate to login page", "expected_result": "Login page loads"}},
        {{"step_number": 2, "description": "Enter valid username and password", "expected_result": "Credentials are accepted"}},
        {{"step_number": 3, "description": "Click login button", "expected_result": "User is redirected to dashboard"}}
      ],
      "expected_outcome": "User successfully logs in",
      "priority": "High",
      "compliance_tags": ["Security"]
    }},
    {{
      "test_id": "TC-REQ-001-002",
      "title": "Verify login with invalid credentials",
      "description": "Ensures system rejects invalid login attempts",
      "preconditions": ["User exists in system"],
      "test_steps": [
        {{"step_number": 1, "description": "Navigate to login page", "expected_result": "Login page loads"}},
        {{"step_number": 2, "description": "Enter invalid username and password", "expected_result": "Credentials are rejected"}},
        {{"step_number": 3, "description": "Attempt to login", "expected_result": "Error message is displayed"}}
      ],
      "expected_outcome": "System prevents unauthorized access",
      "priority": "High",
      "compliance_tags": ["Security"]
    }},
    {{
      "test_id": "TC-REQ-002-001",
      "title": "Verify account lock after 3 failed login attempts",
      "description": "Ensures account is locked after multiple failed login attempts",
      "preconditions": ["User account exists and is active"],
      "test_steps": [
        {{"step_number": 1, "description": "Navigate to login page", "expected_result": "Login page loads"}},
        {{"step_number": 2, "description": "Enter incorrect password for first attempt", "expected_result": "Error message displayed"}},
        {{"step_number": 3, "description": "Enter incorrect password for second attempt", "expected_result": "Error message with warning displayed"}},
        {{"step_number": 4, "description": "Enter incorrect password for third attempt", "expected_result": "Account locked message displayed"}}
      ],
      "expected_outcome": "Account is locked after 3 failed attempts",
      "priority": "High",
      "compliance_tags": ["Security"]
    }}
  ]
}}

CRITICAL REQUIREMENTS:
- Generate AT LEAST 3 test cases per requirement
- Each test case MUST have MINIMUM 3 detailed test steps
- Cover positive cases (valid inputs), negative cases (invalid inputs), and edge cases
- Each step must be atomic and actionable with specific expected results
- Use appropriate compliance tags (HIPAA, Security, FHIR, etc.)
- Make test cases specific and measurable, NOT generic statements
- Ensure proper JSON formatting with no errors
- If multiple requirements are provided, generate separate test cases for each requirement
"""
    
    return prompt.strip()
