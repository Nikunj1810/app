import os
import base64
import tempfile
from typing import Dict, List, Optional
import uuid
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
from models.doubt import DoubtAnswer
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    def _create_chat_session(self) -> LlmChat:
        """Create a new chat session for each request"""
        session_id = f"doubt_session_{uuid.uuid4()}"
        system_message = """You are an expert AI tutor specializing in educational content. Your role is to help students understand concepts by providing clear, step-by-step explanations.

Guidelines:
1. Always provide detailed, step-by-step solutions
2. Explain concepts clearly for educational understanding
3. Use proper mathematical notation when applicable
4. Break down complex problems into manageable steps
5. Provide context and reasoning for each step
6. Be encouraging and supportive in your tone
7. If analyzing an image, describe what you see and then solve the problem

For each response, provide:
- A clear, comprehensive solution
- Step-by-step breakdown of the problem-solving process
- Educational explanations that help understanding

Format your response to be educational and easy to follow."""

        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        
        # Configure for Gemini 2.0-flash
        chat.with_model("gemini", "gemini-2.0-flash")
        chat.with_max_tokens(4096)
        
        return chat
    
    async def process_text_question(self, question: str, subject: str) -> DoubtAnswer:
        """Process a text-based question"""
        try:
            chat = self._create_chat_session()
            
            # Create educational prompt
            prompt = f"""Subject: {subject}
Question: {question}

Please provide a comprehensive, step-by-step solution to this {subject.lower()} question. Make sure to:
1. Explain the approach clearly
2. Show all working steps
3. Provide educational context
4. Make it easy for a student to understand

Please format your response with clear sections and steps."""
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse the response into solution and steps
            solution_text = response.strip()
            steps = self._extract_steps(solution_text)
            
            return DoubtAnswer(
                solution=solution_text,
                steps=steps
            )
            
        except Exception as e:
            logger.error(f"Error processing text question: {str(e)}")
            raise Exception(f"Failed to process question: {str(e)}")
    
    async def process_image_question(self, question: str, subject: str, image_data: str) -> DoubtAnswer:
        """Process a question with an uploaded image"""
        try:
            chat = self._create_chat_session()
            
            # Create educational prompt for image analysis
            prompt = f"""Subject: {subject}
Question: {question if question.strip() else 'Please analyze this image and solve the problem shown.'}

I've uploaded an image that contains a {subject.lower()} problem. Please:
1. Describe what you see in the image
2. Identify the specific problem or question
3. Provide a step-by-step solution
4. Explain each step clearly for educational understanding

Make your response comprehensive and educational."""
            
            # Create image content from base64 data
            image_content = ImageContent(image_base64=image_data)
            
            user_message = UserMessage(
                text=prompt,
                file_contents=[image_content]
            )
            
            response = await chat.send_message(user_message)
            
            # Parse the response into solution and steps
            solution_text = response.strip()
            steps = self._extract_steps(solution_text)
            
            return DoubtAnswer(
                solution=solution_text,
                steps=steps
            )
            
        except Exception as e:
            logger.error(f"Error processing image question: {str(e)}")
            raise Exception(f"Failed to process image question: {str(e)}")
    
    def _extract_steps(self, solution_text: str) -> List[str]:
        """Extract steps from the AI response"""
        steps = []
        
        # Look for numbered steps, bullet points, or step indicators
        lines = solution_text.split('\n')
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for step indicators
            if (line.startswith(('Step', 'step', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) or
                line.startswith(('•', '-', '*')) or
                'step' in line.lower()[:10]):
                if current_step:
                    steps.append(current_step.strip())
                current_step = line
            else:
                if current_step:
                    current_step += " " + line
                elif line and len(steps) < 6:  # Add first few meaningful lines as steps
                    steps.append(line)
        
        if current_step:
            steps.append(current_step.strip())
        
        # If no clear steps found, create basic steps from key sentences
        if not steps:
            sentences = [s.strip() for s in solution_text.split('.') if s.strip()]
            steps = sentences[:6]  # Take first 6 meaningful sentences
        
        # Clean up steps
        cleaned_steps = []
        for step in steps[:8]:  # Limit to 8 steps max
            if len(step) > 10 and step not in cleaned_steps:
                cleaned_steps.append(step)
        
        return cleaned_steps if cleaned_steps else ["Solution provided above with detailed explanation"]