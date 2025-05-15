import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

class GeminiService:
    """Service for interacting with Google's Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Default to Gemini Pro model
        self.model_name = "gemini-2.5-flash-preview-04-17"
        self.model = genai.GenerativeModel(self.model_name)
    
    async def generate_email(
        self, 
        job_description: str, 
        projects: List[Dict[str, Any]], 
        user_info: Dict[str, Any],
        language: str = "english"
    ) -> str:
        """
        Generate a personalized email for HR using the Gemini API
        
        Args:
            job_description: The job description text
            projects: List of GitHub projects with details
            user_info: User information (name, contact details)
            language: The language to generate the email in ("english" or "turkish")
            
        Returns:
            The generated email text
        """
        try:
            # Construct the prompt for Gemini
            prompt = self._construct_email_prompt(job_description, projects, user_info, language)
            
            # Generate the email
            response = self.model.generate_content(prompt)
            
            # Extract and return the generated text
            if hasattr(response, 'text'):
                return response.text
            else:
                # Handle different response formats
                return str(response)
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate email: {str(e)}"
            )
    
    def _construct_email_prompt(
        self, 
        job_description: str, 
        projects: List[Dict[str, Any]], 
        user_info: Dict[str, Any],
        language: str
    ) -> str:
        """
        Construct a detailed prompt for the Gemini API
        
        Args:
            job_description: The job description text
            projects: List of GitHub projects with details
            user_info: User information (name, contact details)
            language: The language to generate the email in
            
        Returns:
            A formatted prompt string
        """
        # Start with basic instructions
        prompt = f"""
You are a professional job application assistant. Your task is to write a personalized email to a hiring manager for a job application.

The email should be in {language.capitalize()} language.

## Job Description:
{job_description}

## Applicant Information:
- Name: {user_info.get('username', 'Applicant')}
- Email: {user_info.get('email', 'applicant@example.com')}

## Relevant Projects:
"""
        
        # Add project details
        for i, project in enumerate(projects, 1):
            prompt += f"""
Project {i}: {project.get('name', 'Unnamed Project')}
- Description: {project.get('description', 'No description available')}
- Language: {project.get('language', 'Not specified')}
- GitHub URL: {project.get('html_url', 'No URL available')}
"""
            
            # Add README content if available (truncated to avoid very long prompts)
            readme = project.get('readme_content', '')
            if readme:
                # Truncate README to a reasonable length (first 500 chars)
                truncated_readme = readme[:500] + ("..." if len(readme) > 500 else "")
                prompt += f"- README Summary: {truncated_readme}\n"
        
        # Add instructions for email generation
        prompt += f"""
## Instructions:
1. Write a professional email addressed to the hiring manager (use "Dear Hiring Manager" or appropriate greeting in {language}).
2. Start with a brief introduction of yourself.
3. Express interest in the position and mention how you found the job posting.
4. Analyze the job description and explain how your skills and experience match the requirements.
5. Highlight the relevant projects listed above, explaining how they demonstrate your qualifications for this role.
6. For each project, explain what technologies were used and what problems were solved.
7. Connect your experience directly to the job requirements.
8. Include a call to action (e.g., request for an interview).
9. End with a professional closing.
10. Include your name and contact information in the signature.
11. The entire email should be in {language} language.
12. Make the email personalized, professional, and concise (around 400-500 words).

Write the complete email now:
"""
        
        return prompt
