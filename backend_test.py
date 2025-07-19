#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for DoubSolver AI-powered doubt solver
Tests all enhanced features including OCR, image upload, authentication, and chat functionality
"""

import asyncio
import aiohttp
import json
import base64
import os
import sys
from typing import Dict, Any, Optional
import tempfile
from PIL import Image, ImageDraw, ImageFont
import io

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://7754185c-acae-4cb1-954f-554488d57a1e.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_id = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error
        })
    
    def create_test_image_base64(self, text: str = "2x + 5 = 15\nSolve for x") -> str:
        """Create a test image with mathematical text for OCR testing"""
        try:
            # Create a simple image with text
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a font, fallback to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Draw text on image
            draw.text((20, 50), text, fill='black', font=font)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = buffer.getvalue()
            
            return base64.b64encode(img_data).decode('utf-8')
        except Exception as e:
            print(f"Warning: Could not create test image: {e}")
            # Return a minimal base64 encoded 1x1 PNG as fallback
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    async def test_health_check(self):
        """Test basic API health check"""
        try:
            async with self.session.get(f"{API_BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Health Check", True, f"API version: {data.get('version', 'unknown')}")
                else:
                    self.log_test("Health Check", False, f"Status: {response.status}")
        except Exception as e:
            self.log_test("Health Check", False, error=str(e))
    
    async def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            user_data = {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@example.com",
                "password": "SecurePass123!"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/auth/register",
                json=user_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("access_token"):
                        self.auth_token = data["access_token"]
                        self.test_user_id = data["user"]["id"]
                        self.log_test("User Registration", True, f"User ID: {self.test_user_id}")
                    else:
                        self.log_test("User Registration", False, "Missing success flag or token")
                else:
                    error_data = await response.text()
                    self.log_test("User Registration", False, f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("User Registration", False, error=str(e))
    
    async def test_user_login(self):
        """Test user login endpoint"""
        try:
            login_data = {
                "email": "sarah.johnson@example.com",
                "password": "SecurePass123!"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("access_token"):
                        # Update token in case it's different
                        self.auth_token = data["access_token"]
                        self.log_test("User Login", True, f"Token received")
                    else:
                        self.log_test("User Login", False, "Missing success flag or token")
                else:
                    error_data = await response.text()
                    self.log_test("User Login", False, f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("User Login", False, error=str(e))
    
    async def test_protected_endpoint(self):
        """Test JWT authentication on protected endpoint"""
        if not self.auth_token:
            self.log_test("JWT Authentication", False, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(
                f"{API_BASE_URL}/auth/me",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("JWT Authentication", True, f"User: {data.get('name', 'unknown')}")
                else:
                    self.log_test("JWT Authentication", False, f"Status: {response.status}")
        except Exception as e:
            self.log_test("JWT Authentication", False, error=str(e))
    
    async def test_text_question_processing(self):
        """Test POST /api/questions/text endpoint"""
        if not self.auth_token:
            self.log_test("Text Question Processing", False, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            question_data = {
                "question": "What is the derivative of x^2 + 3x + 5?",
                "subject": "mathematics"
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/questions/text",
                json=question_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("answer") and data.get("answer", {}).get("solution"):
                        self.log_test("Text Question Processing", True, 
                                    f"Question processed, status: {data.get('status')}")
                    else:
                        self.log_test("Text Question Processing", False, "No answer generated")
                else:
                    error_data = await response.text()
                    self.log_test("Text Question Processing", False, 
                                f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("Text Question Processing", False, error=str(e))
    
    async def test_image_question_processing(self):
        """Test POST /api/questions/image endpoint with OCR"""
        if not self.auth_token:
            self.log_test("Image Question Processing", False, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create test image with mathematical content
            test_image_b64 = self.create_test_image_base64("Find the value of x: 2x + 8 = 20")
            
            # Convert base64 to bytes for multipart upload
            image_bytes = base64.b64decode(test_image_b64)
            
            # Create multipart form data
            data = aiohttp.FormData()
            data.add_field('file', image_bytes, filename='test_math.png', content_type='image/png')
            data.add_field('question', 'Please solve this mathematical equation')
            data.add_field('subject', 'mathematics')
            
            async with self.session.post(
                f"{API_BASE_URL}/questions/image",
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    has_ocr_data = data.get("ocr_data") is not None
                    has_answer = data.get("answer") and data.get("answer", {}).get("solution")
                    
                    self.log_test("Image Question Processing", True, 
                                f"OCR data: {has_ocr_data}, Answer: {has_answer}, Status: {data.get('status')}")
                else:
                    error_data = await response.text()
                    self.log_test("Image Question Processing", False, 
                                f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("Image Question Processing", False, error=str(e))
    
    async def test_ocr_functionality(self):
        """Test OCR integration specifically"""
        if not self.auth_token:
            self.log_test("OCR Integration", False, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create test image with clear text for OCR
            test_image_b64 = self.create_test_image_base64("Calculate: 15 + 25 = ?")
            image_bytes = base64.b64decode(test_image_b64)
            
            # Test with different file types
            data = aiohttp.FormData()
            data.add_field('file', image_bytes, filename='ocr_test.png', content_type='image/png')
            data.add_field('question', '')  # Empty question to rely on OCR
            data.add_field('subject', 'mathematics')
            
            async with self.session.post(
                f"{API_BASE_URL}/questions/image",
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ocr_data = data.get("ocr_data", {})
                    extracted_text = ocr_data.get("extracted_text", "")
                    
                    if extracted_text:
                        self.log_test("OCR Integration", True, 
                                    f"Extracted text: '{extracted_text[:50]}...', Method: {ocr_data.get('preprocessing_used')}")
                    else:
                        self.log_test("OCR Integration", False, "No text extracted from image")
                else:
                    error_data = await response.text()
                    self.log_test("OCR Integration", False, 
                                f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("OCR Integration", False, error=str(e))
    
    async def test_file_upload_validation(self):
        """Test enhanced image upload handling with validation"""
        if not self.auth_token:
            self.log_test("File Upload Validation", False, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test 1: Invalid file type
            invalid_data = aiohttp.FormData()
            invalid_data.add_field('file', b'invalid content', filename='test.txt', content_type='text/plain')
            invalid_data.add_field('question', 'Test question')
            invalid_data.add_field('subject', 'mathematics')
            
            async with self.session.post(
                f"{API_BASE_URL}/questions/image",
                data=invalid_data,
                headers=headers
            ) as response:
                if response.status == 400:
                    self.log_test("File Upload Validation - Invalid Type", True, "Correctly rejected invalid file type")
                else:
                    self.log_test("File Upload Validation - Invalid Type", False, 
                                f"Should reject invalid file type, got status: {response.status}")
            
            # Test 2: Valid file type
            valid_image = self.create_test_image_base64("Test equation: x + 5 = 10")
            image_bytes = base64.b64decode(valid_image)
            
            valid_data = aiohttp.FormData()
            valid_data.add_field('file', image_bytes, filename='valid.png', content_type='image/png')
            valid_data.add_field('question', 'Solve this equation')
            valid_data.add_field('subject', 'mathematics')
            
            async with self.session.post(
                f"{API_BASE_URL}/questions/image",
                data=valid_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    self.log_test("File Upload Validation - Valid Type", True, "Correctly accepted valid image")
                else:
                    error_data = await response.text()
                    self.log_test("File Upload Validation - Valid Type", False, 
                                f"Should accept valid image, got status: {response.status}, Response: {error_data}")
                    
        except Exception as e:
            self.log_test("File Upload Validation", False, error=str(e))
    
    async def test_user_question_history(self):
        """Test GET /api/questions/user/:userId endpoint"""
        if not self.auth_token or not self.test_user_id:
            self.log_test("User Question History", False, "No auth token or user ID available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(
                f"{API_BASE_URL}/questions/user/{self.test_user_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_test("User Question History", True, 
                                    f"Retrieved {len(data)} questions from history")
                    else:
                        self.log_test("User Question History", False, "Response is not a list")
                else:
                    error_data = await response.text()
                    self.log_test("User Question History", False, 
                                f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("User Question History", False, error=str(e))
    
    async def test_chat_functionality(self):
        """Test POST /api/chat/send endpoint"""
        if not self.auth_token:
            self.log_test("Chat Functionality", False, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            chat_data = {
                "message": "I need help understanding calculus derivatives",
                "doubt_id": None
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/chat/send",
                json=chat_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") and data.get("sender_type"):
                        self.log_test("Chat Functionality", True, 
                                    f"Message sent, sender: {data.get('sender_type')}")
                    else:
                        self.log_test("Chat Functionality", False, "Invalid chat response format")
                else:
                    error_data = await response.text()
                    self.log_test("Chat Functionality", False, 
                                f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("Chat Functionality", False, error=str(e))
    
    async def test_chat_message_retrieval(self):
        """Test GET /api/chat/messages endpoint"""
        if not self.auth_token:
            self.log_test("Chat Message Retrieval", False, "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(
                f"{API_BASE_URL}/chat/messages",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_test("Chat Message Retrieval", True, 
                                    f"Retrieved {len(data)} chat messages")
                    else:
                        self.log_test("Chat Message Retrieval", False, "Response is not a list")
                else:
                    error_data = await response.text()
                    self.log_test("Chat Message Retrieval", False, 
                                f"Status: {response.status}, Response: {error_data}")
        except Exception as e:
            self.log_test("Chat Message Retrieval", False, error=str(e))
    
    async def test_unauthorized_access(self):
        """Test that protected endpoints reject unauthorized requests"""
        try:
            # Test without auth token
            async with self.session.get(f"{API_BASE_URL}/auth/me") as response:
                if response.status == 401:
                    self.log_test("Unauthorized Access Protection", True, "Correctly rejected unauthorized request")
                else:
                    self.log_test("Unauthorized Access Protection", False, 
                                f"Should reject unauthorized request, got status: {response.status}")
        except Exception as e:
            self.log_test("Unauthorized Access Protection", False, error=str(e))
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*60}")
        print(f"BACKEND TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}")
                    if result["error"]:
                        print(f"   Error: {result['error']}")
        
        print(f"{'='*60}")
        
        return passed_tests, failed_tests

async def run_all_tests():
    """Run all backend tests"""
    print(f"Starting Backend API Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"{'='*60}")
    
    async with BackendTester() as tester:
        # Core API tests
        await tester.test_health_check()
        
        # Authentication tests
        await tester.test_user_registration()
        await tester.test_user_login()
        await tester.test_protected_endpoint()
        await tester.test_unauthorized_access()
        
        # Question processing tests
        await tester.test_text_question_processing()
        await tester.test_image_question_processing()
        await tester.test_ocr_functionality()
        await tester.test_file_upload_validation()
        
        # User data tests
        await tester.test_user_question_history()
        
        # Chat functionality tests
        await tester.test_chat_functionality()
        await tester.test_chat_message_retrieval()
        
        # Print summary
        passed, failed = tester.print_summary()
        
        return passed, failed

if __name__ == "__main__":
    try:
        passed, failed = asyncio.run(run_all_tests())
        sys.exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        sys.exit(1)