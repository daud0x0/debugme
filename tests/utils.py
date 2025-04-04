import google.generativeai as genai
from django.conf import settings
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def generate_questions(subtopic: str, difficulty_level: int = 1, num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Generate multiple choice questions using Gemini API with improved error handling and response formatting.
    
    Args:
        subtopic: The subtopic to generate questions about
        difficulty_level: Difficulty level (1-5)
        num_questions: Number of questions to generate
        
    Returns:
        List of question dictionaries with text, options, correct answer, and explanation
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key="AIzaSyBHsQiaVTGtu6YFQFXxdu08my5QuKUK6yQ")
        
        # Create a model instance
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        
        # Create a detailed prompt for better question generation
        prompt = f"""
        You are an expert teacher creating a test about {subtopic}.
        Generate {num_questions} high-quality multiple choice questions.
        Difficulty level: {difficulty_level} (1-5, where 1 is basic and 5 is advanced).
        
        The response MUST be a valid JSON array containing question objects.
        DO NOT include any explanatory text before or after the JSON array.
        
        Each question object must have this exact structure:
        {{
            "question": "Question text here",
            "options": {{
                "A": "First option",
                "B": "Second option",
                "C": "Third option",
                "D": "Fourth option"
            }},
            "correct_answer": "A",
            "explanation": "Explanation text here"
        }}
        
        Question Guidelines:
        1. Questions should test understanding, not just memorization
        2. Each option must be unique and plausible
        3. Distractors (wrong options) should be common misconceptions
        4. Questions should be clear, concise, and unambiguous
        5. Explanations should be detailed and educational
        6. Use proper technical terminology
        7. Include practical, real-world examples where applicable
        8. Ensure questions build on fundamental concepts
        
        For difficulty levels:
        - Level 1: Basic concept understanding
        - Level 2: Application of concepts
        - Level 3: Analysis and problem-solving
        - Level 4: Integration of multiple concepts
        - Level 5: Advanced problem-solving and edge cases
        
        Return ONLY the JSON array with no additional text.
        """
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Debug: Print raw response
        logger.debug(f"Raw Gemini response: {response.text}")
        
        # Clean the response text to ensure it's valid JSON
        response_text = response.text.strip()
        if not response_text.startswith('['):
            # If response is not a JSON array, try to extract JSON portion
            try:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    response_text = response_text[start_idx:end_idx]
                else:
                    raise ValueError("Could not find JSON array in response")
            except Exception as e:
                logger.error(f"Failed to extract JSON from response: {e}")
                logger.error(f"Response text: {response_text}")
                return []
        
        try:
            questions = json.loads(response_text)
            if not isinstance(questions, list):
                raise ValueError("Response is not a list")
            
            # Validate each question has required fields
            for q in questions:
                if not all(k in q for k in ['question', 'options', 'correct_answer', 'explanation']):
                    raise ValueError("Missing required fields in question")
                if not all(opt in q['options'] for opt in ['A', 'B', 'C', 'D']):
                    raise ValueError("Missing options in question")
                if q['correct_answer'] not in ['A', 'B', 'C', 'D']:
                    raise ValueError("Invalid correct answer")
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini API response: {e}")
            return []
        except ValueError as e:
            logger.error(f"Invalid question format: {e}")
            return []
            
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return []

def calculate_difficulty_level(user_performance: float) -> int:
    """
    Calculate the next difficulty level based on user performance.
    
    Args:
        user_performance: User's average score (0-100)
        
    Returns:
        Difficulty level (1-5)
    """
    if user_performance >= 90:
        return min(5, 3)  # Cap at level 3 for now
    elif user_performance >= 75:
        return 2
    else:
        return 1 