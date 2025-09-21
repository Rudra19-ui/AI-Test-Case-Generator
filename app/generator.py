import re
import logging
from typing import List, Tuple

from app.models import Requirement, TestCase, TestStep
from app.llm_client import generate, create_test_case_prompt, safe_parse_json
from app.vectorstore import vectorstore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def split_requirements(text: str) -> List[Requirement]:
    """Split requirements text into individual Requirement objects."""
    requirements = []
    
    if not text or not text.strip():
        return requirements
    
    # Pattern 1: REQ-XXX: format
    req_pattern = r'REQ-(\d+):\s*(.+?)(?=REQ-\d+:|$)'
    matches = re.findall(req_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if matches:
        for req_num, req_text in matches:
            req_text = req_text.strip()
            if req_text:
                requirements.append(Requirement(
                    req_id=f"REQ-{req_num}",
                    text=req_text
                ))
        return requirements
    
    # Pattern 2: Numbered list (1., 2., etc.)
    numbered_pattern = r'(\d+)\.\s*(.+?)(?=\d+\.|$)'
    matches = re.findall(numbered_pattern, text, re.DOTALL)
    
    if matches:
        for req_num, req_text in matches:
            req_text = req_text.strip()
            if req_text:
                requirements.append(Requirement(
                    req_id=f"REQ-{req_num}",
                    text=req_text
                ))
        return requirements
    
    # Pattern 3: Split by paragraphs (fallback)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    for i, paragraph in enumerate(paragraphs, 1):
        # Skip if it looks like a header or comment
        if paragraph.startswith('#') or paragraph.startswith('//'):
            continue
        
        requirements.append(Requirement(
            req_id=f"REQ-{i:03d}",
            text=paragraph
        ))
    
    return requirements

async def generate_multiple_test_cases(requirement: Requirement) -> List[TestCase]:
    """Generate multiple test cases for a single requirement."""
    try:
        # Get relevant compliance tags
        compliance_snippets = await vectorstore.query(requirement.text, top_k=3)
        compliance_tags = [snippet.tag for snippet in compliance_snippets]
        
        # Create prompt
        prompt = create_test_case_prompt(requirement.text, compliance_tags)
        
        # Generate test cases
        response = await generate(prompt)
        
        if not response:
            logger.error(f"Failed to generate test cases for requirement {requirement.req_id}")
            return [create_fallback_test_case(requirement)]
        
        # Parse the response
        response_data = safe_parse_json(response)
        
        if not response_data:
            logger.error(f"Failed to parse test cases JSON for requirement {requirement.req_id}")
            return [create_fallback_test_case(requirement)]
        
        # Handle the new format with multiple test cases
        test_cases_data = response_data.get('test_cases', [])
        if not test_cases_data:
            logger.error(f"No test cases found in response for requirement {requirement.req_id}")
            return [create_fallback_test_case(requirement)]
        
        test_cases = []
        for test_case_data in test_cases_data:
            # Create TestCase object
            test_steps = []
            for step_data in test_case_data.get('test_steps', []):
                test_steps.append(TestStep(
                    step_number=step_data.get('step_number', 1),
                    description=step_data.get('description', ''),
                    expected_result=step_data.get('expected_result', '')
                ))
            
            test_case = TestCase(
                test_id=test_case_data.get('test_id', f"TC-{requirement.req_id}-001"),
                title=test_case_data.get('title', f"Test for {requirement.req_id}"),
                description=test_case_data.get('description', requirement.text),
                preconditions=test_case_data.get('preconditions', []),
                test_steps=test_steps,
                expected_outcome=test_case_data.get('expected_outcome', 'Test passes'),
                priority=test_case_data.get('priority', 'Medium'),
                requirement_id=requirement.req_id,
                compliance_tags=test_case_data.get('compliance_tags', compliance_tags)
            )
            test_cases.append(test_case)
        
        logger.info(f"Generated {len(test_cases)} test cases for requirement {requirement.req_id}")
        return test_cases
        
    except Exception as e:
        logger.error(f"Error generating test cases for requirement {requirement.req_id}: {str(e)}")
        return [create_fallback_test_case(requirement)]

def create_fallback_test_case(requirement: Requirement) -> TestCase:
    """Create a basic fallback test case when generation fails."""
    return TestCase(
        test_id=f"TC-{requirement.req_id}-001",
        title=f"Basic Test for {requirement.req_id}",
        description=f"Basic test case for requirement: {requirement.text}",
        preconditions=["System is available", "User has appropriate permissions"],
        test_steps=[
            TestStep(
                step_number=1,
                description="Execute the functionality described in the requirement",
                expected_result="Functionality works as expected"
            )
        ],
        expected_outcome="Requirement is satisfied",
        priority="Medium",
        requirement_id=requirement.req_id,
        compliance_tags=[]
    )

async def generate_test_cases(requirements_text: str) -> Tuple[List[TestCase], List[Requirement]]:
    """Generate test cases from requirements text."""
    logger.info("Starting test case generation...")
    
    # Split requirements
    requirements = await split_requirements(requirements_text)
    logger.info(f"Split into {len(requirements)} requirements")
    
    if not requirements:
        logger.warning("No requirements found in the provided text")
        return [], []
    
    # Generate test cases
    test_cases = []
    for requirement in requirements:
        requirement_test_cases = await generate_multiple_test_cases(requirement)
        test_cases.extend(requirement_test_cases)
    
    logger.info(f"Generated {len(test_cases)} test cases")
    return test_cases, requirements
