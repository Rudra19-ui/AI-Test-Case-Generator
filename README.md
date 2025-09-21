# AI Test Case Generator

A powerful web application that generates comprehensive test cases from software requirements using AI technology. This project combines a FastAPI backend with a modern React frontend to provide an intuitive interface for automated test case generation.

## ✨ Latest Updates
- Enhanced test case generation with multiple detailed test cases per requirement
- Improved JSON formatting for better integration
- Added TC-REQ-XXX-YYY test ID format for better traceability

## 📋 Project Overview

The AI Test Case Generator is designed to streamline the software testing process by automatically creating detailed test cases from natural language requirements. The system uses OpenAI's GPT models to analyze requirements and generate structured test cases with step-by-step instructions, expected outcomes, and compliance tags.

### How It Works

1. **User Input**: Users enter software requirements in natural language through a web interface
2. **AI Processing**: The backend sends requirements to OpenAI's API for analysis
3. **Test Case Generation**: AI generates comprehensive test cases with detailed steps
4. **Compliance Tagging**: The system automatically tags test cases with relevant compliance standards (HIPAA, FHIR, etc.)
5. **Display Results**: Generated test cases are presented in a clean, organized format

## 🛠️ Tech Stack

### Backend
- **Python 3.12+** - Core programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation and settings management
- **OpenAI API** - AI-powered text generation
- **Sentence Transformers** - Embedding models for compliance tagging
- **FAISS** - Vector similarity search
- **Uvicorn** - ASGI server

### Frontend
- **React 19** - User interface library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router v7** - Client-side routing

### Development Tools
- **pytest** - Testing framework
- **ESLint/Prettier** - Code formatting and linting

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.12 or higher**
- **Node.js 18 or higher**
- **npm 9 or higher**
- **OpenAI API Key** (sign up at [OpenAI](https://platform.openai.com/))

### Backend Setup

1. **Navigate to the project directory:**
   ```bash
   cd ai-testcase-generator
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your-openai-api-key-here"
   
   # Linux/Mac
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

## 🏃‍♂️ Running the Project

### Start the Backend Server

1. **Navigate to the backend directory:**
   ```bash
   cd ai-testcase-generator
   ```

2. **Set your OpenAI API key:**
   ```bash
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Run the FastAPI server:**
   ```bash
   python main.py
   ```

   The backend will be available at: **http://127.0.0.1:8000**

### Start the Frontend Server

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at: **http://localhost:5173**

### Access the Application

Open your web browser and navigate to **http://localhost:5173** to access the AI Test Case Generator.

## 📁 Project Structure

```
ai-testcase-generator/
├── app/                          # Backend application code
│   ├── __init__.py
│   ├── config.py                 # Configuration settings
│   ├── generator.py              # Test case generation logic
│   ├── llm_client.py             # OpenAI API integration
│   ├── models.py                 # Pydantic data models
│   ├── vectorstore.py            # Vector embeddings for compliance
│   └── schema/
│       └── testcase_schema.json  # JSON schema for test cases
├── frontend/                     # React frontend application
│   ├── app/
│   │   ├── components/
│   │   │   └── TestCaseGenerator.tsx  # Main React component
│   │   ├── routes/
│   │   │   └── home.tsx          # Home page route
│   │   ├── app.css               # Global styles with Tailwind
│   │   └── root.tsx              # Root layout component
│   ├── public/                   # Static assets
│   ├── package.json              # Node.js dependencies
│   └── vite.config.ts            # Vite configuration
├── sample_data/                  # Sample data files
│   ├── compliance_snippets.json  # Compliance reference data
│   └── sample_requirements.txt   # Example requirements
├── tests/                        # Test files
│   └── test_generator.py         # Unit tests
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### Key Files Explained

- **`main.py`**: FastAPI application entry point with API endpoints
- **`app/generator.py`**: Core logic for parsing requirements and generating test cases
- **`app/llm_client.py`**: Handles communication with OpenAI API
- **`app/vectorstore.py`**: Manages compliance snippet embeddings
- **`frontend/app/components/TestCaseGenerator.tsx`**: Main React component for the UI
- **`requirements.txt`**: Python package dependencies
- **`frontend/package.json`**: Node.js package dependencies

## 🔌 API Endpoints

### Generate Test Cases

**Endpoint:** `POST /generate`

**Description:** Generates test cases from software requirements text.

**Request Body:**
```json
{
  "text": "The system shall allow users to login with username and password"
}
```

**Response:**
```json
{
  "test_cases": [
    {
      "test_id": "TC-REQ-001-001",
      "title": "Verify User Login with Valid Credentials",
      "description": "Test that users can successfully login with valid username and password",
      "preconditions": [
        "User account exists in the system",
        "System is accessible"
      ],
      "test_steps": [
        {
          "step_number": 1,
          "description": "Navigate to the login page",
          "expected_result": "Login page is displayed"
        },
        {
          "step_number": 2,
          "description": "Enter valid username",
          "expected_result": "Username is accepted"
        },
        {
          "step_number": 3,
          "description": "Enter valid password",
          "expected_result": "Password is accepted"
        },
        {
          "step_number": 4,
          "description": "Click login button",
          "expected_result": "User is successfully logged in"
        }
      ],
      "expected_outcome": "User is redirected to the dashboard",
      "priority": "High",
      "requirement_id": "REQ-001",
      "compliance_tags": ["Security"],
      "created_at": "2025-09-21T00:00:00"
    }
  ],
  "count": 1,
  "source_requirements": [...]
}
```

### Health Check

**Endpoint:** `GET /health`

**Description:** Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### API Documentation

**Endpoint:** `GET /docs`

**Description:** Interactive API documentation (Swagger UI).

## 🎨 UI Guide

### Main Interface

The application features a clean, modern interface built with Tailwind CSS:

1. **Header Section**: Displays the application title and description
2. **Input Area**: Large textarea for entering software requirements
3. **Generate Button**: Triggers test case generation with loading animation
4. **Results Section**: Displays generated test cases in organized cards

### Using the Application

1. **Enter Requirements**: Type or paste your software requirements into the text area
   - Example: "The system shall encrypt all user passwords using bcrypt"
   - Multiple requirements can be entered at once

2. **Generate Test Cases**: Click the "Generate Test Cases" button
   - A loading spinner will appear while the AI processes your request
   - The process typically takes 5-15 seconds depending on complexity

3. **Review Results**: Generated test cases are displayed as cards showing:
   - **Test ID**: Unique identifier for the test case
   - **Title**: Descriptive name of the test case
   - **Description**: Detailed explanation of what the test verifies
   - **Preconditions**: Prerequisites for running the test
   - **Test Steps**: Step-by-step instructions with expected results
   - **Priority Level**: High, Medium, or Low priority
   - **Compliance Tags**: Relevant compliance standards

### Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Validation**: Input validation with helpful error messages
- **Loading States**: Visual feedback during API calls
- **Error Handling**: Graceful error messages for failed requests
- **Compliance Tagging**: Automatic tagging with relevant standards (HIPAA, FHIR, etc.)

## 🔧 Troubleshooting

### Common Issues

#### 1. Missing OpenAI API Key
**Error:** `Warning: OPENAI_API_KEY not set. LLM functionality will not work.`

**Solution:**
```bash
# Set your API key
$env:OPENAI_API_KEY="your-api-key-here"
```

#### 2. Backend Connection Issues
**Error:** `Unable to connect to the remote server`

**Solutions:**
- Ensure the backend is running on `http://127.0.0.1:8000`
- Check that no firewall is blocking the connection
- Verify the backend started successfully (look for "Uvicorn running on http://0.0.0.0:8000")

#### 3. Frontend Build Errors
**Error:** `npm error code ENOENT`

**Solutions:**
- Navigate to the correct directory: `cd frontend`
- Install dependencies: `npm install`
- Clear npm cache: `npm cache clean --force`

#### 4. CORS Issues
**Error:** Cross-origin request blocked

**Solution:** The backend includes CORS middleware to allow frontend connections. If issues persist, check that both servers are running on the correct ports.

#### 5. Python Package Installation Issues
**Error:** `Failed to import transformers`

**Solution:**
```bash
# Install compatible packages
pip install tf-keras
pip install --upgrade sentence-transformers
```

#### 6. Port Already in Use
**Error:** `Address already in use`

**Solutions:**
- Kill existing processes: `taskkill /f /im python.exe` (Windows)
- Use different ports by modifying the configuration
- Restart your computer to clear all port bindings

### Getting Help

If you encounter issues not covered here:

1. Check the console output for detailed error messages
2. Verify all dependencies are installed correctly
3. Ensure your OpenAI API key is valid and has sufficient credits
4. Check that both frontend and backend servers are running simultaneously

## 🚀 Future Enhancements

### Planned Features

- **Export Functionality**: Export test cases to Excel, CSV, or PDF formats
- **User Authentication**: User accounts and saved requirement templates
- **Test Case Templates**: Pre-defined templates for different types of applications
- **Integration**: Connect with test management tools (Jira, TestRail, etc.)
- **Batch Processing**: Upload multiple requirement documents
- **Custom Compliance Standards**: Add custom compliance frameworks
- **Test Case Versioning**: Track changes and maintain test case history
- **Collaboration**: Share and comment on generated test cases
- **Advanced AI Models**: Support for different AI models and providers
- **API Rate Limiting**: Implement rate limiting for production use

### Technical Improvements

- **Database Integration**: Store generated test cases persistently
- **Caching**: Implement Redis caching for faster responses
- **Microservices**: Split into smaller, focused services
- **Docker Support**: Containerize the application for easy deployment
- **CI/CD Pipeline**: Automated testing and deployment
- **Monitoring**: Add logging and monitoring capabilities
- **Performance Optimization**: Optimize AI model usage and response times

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

For support and questions, please open an issue in the project repository or contact the development team.

---

**Happy Testing! 🧪✨**
