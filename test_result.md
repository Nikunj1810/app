#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Enhance the existing FastAPI backend for an AI-powered doubt solver web app. The current system has basic functionality with Gemini AI integration. 
  Need to add:
  - OpenAI API integration alongside Gemini (dual AI provider support)
  - Enhanced image upload handling with OCR capabilities using Tesseract
  - Complete API endpoints matching Node.js + Express requirements:
    * POST /api/questions/text - Process text questions
    * POST /api/questions/image - Process image questions with OCR
    * GET /api/questions/user/:userId - Get user question history  
    * POST /api/auth/register & /api/auth/login - JWT authentication
    * Optional: POST /api/chat/send - Chat functionality
  - Better file upload handling (equivalent to Multer)
  - Clean MVC structure maintenance
  - MongoDB integration with proper models (User, Question, Chat logs)

backend:
  - task: "OpenAI Integration Setup"
    implemented: false
    working: false
    file: "services/ai_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: false
        agent: "main"
        comment: "Need OpenAI API key from user before implementation"

  - task: "OCR Integration with Tesseract"
    implemented: false
    working: false
    file: "services/ocr_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: false
        agent: "main"
        comment: "Need to install and configure Tesseract OCR library"

  - task: "Enhanced Image Upload Handling"
    implemented: false
    working: false
    file: "routes/doubts.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: false
        agent: "main"
        comment: "Need to improve file upload with better validation"

  - task: "API Endpoints Matching Requirements"
    implemented: true
    working: true
    file: "routes/*.py"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Basic endpoints exist, need to verify they match exact requirements"

  - task: "Chat Functionality (Optional)"
    implemented: false
    working: false
    file: "routes/chat.py"
    stuck_count: 0
    priority: "low"
    needs_retesting: true
    status_history:
      - working: false
        agent: "main"
        comment: "Optional feature - will implement if time permits"

frontend:
  - task: "Frontend Integration Testing"
    implemented: true
    working: true
    file: "src/components/*"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "Frontend exists and works with current backend, need to test with enhancements"

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "OpenAI Integration Setup"
    - "OCR Integration with Tesseract"
    - "Enhanced Image Upload Handling"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Starting backend enhancement. Current FastAPI backend is functional with Gemini AI. Need to add OpenAI, OCR, and improve image handling. Waiting for OpenAI API key from user."