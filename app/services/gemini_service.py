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
    
    async def suggest_projects(
        self,
        job_description: str,
        all_projects: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Suggest relevant GitHub projects based on job description
        
        Args:
            job_description: The job description text
            all_projects: List of all GitHub projects with details
            
        Returns:
            List of suggested project IDs
        """
        try:
            # Construct the prompt for Gemini
            prompt = self._construct_suggestion_prompt(job_description, all_projects)
            
            # Generate the suggestions
            response = self.model.generate_content(prompt)
            
            # Extract and return the suggested project IDs
            if hasattr(response, 'text'):
                suggested_ids = self._parse_suggested_projects(response.text, all_projects)
                return suggested_ids
            else:
                # Handle different response formats
                suggested_ids = self._parse_suggested_projects(str(response), all_projects)
                return suggested_ids
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to suggest projects: {str(e)}"
            )
    
    def _construct_suggestion_prompt(
        self,
        job_description: str,
        all_projects: List[Dict[str, Any]]
    ) -> str:
        """
        Construct a prompt for project suggestion
        
        Args:
            job_description: The job description text
            all_projects: List of all GitHub projects with details
            
        Returns:
            A formatted prompt string
        """
        prompt = f"""
You are a professional job application assistant. Your task is to analyze a job description and suggest the most relevant GitHub projects from a user's repository that would best showcase their skills for this specific job.

## Job Description:
{job_description}

## Available GitHub Projects:
"""
        
        # Add all project details and provide a reference list of names
        name_list = []
        for i, project in enumerate(all_projects, 1):
            project_name = project.get('name', 'Unnamed Project')
            name_list.append(project_name)
            
            prompt += f"""
Project {i}: {project_name}
- Description: {project.get('description', 'No description available')}
- Language: {project.get('language', 'Not specified')}
- Topics: {', '.join(project.get('topics', ['No topics']))}
"""
            
            # Add README content if available (truncated to avoid very long prompts)
            readme = project.get('readme_content', '')
            if readme:
                # Truncate README to a reasonable length
                truncated_readme = readme[:300] + ("..." if len(readme) > 300 else "")
                prompt += f"- README Summary: {truncated_readme}\n"
        
        # Add instructions for suggestion generation with explicit name reference
        prompt += f"""
## Available Project Names for Reference:
{', '.join(name_list)}

## Instructions:
1. Analyze the job description to identify key skills, technologies, and requirements.
2. Evaluate each GitHub project for relevance to the job description.
3. Select 3-5 projects that best demonstrate the candidate's qualifications for this role.
4. Use EXACT project names from the list above - do not modify or create new names.
5. For each selected project, briefly explain why it's relevant to the job.
6. Return your suggestions in the following JSON format:
{{
  "suggested_projects": [
    {{
      "name": "exact_project_name_from_above_list",
      "reason": "Brief explanation of relevance"
    }},
    {{
      "name": "another_exact_project_name",
      "reason": "Brief explanation of relevance"
    }}
  ]
}}

Provide only the JSON response without any additional text. Make sure to use the exact project names provided in the available projects list.
"""
        
        return prompt
    
    def _parse_suggested_projects(self, response_text: str, all_projects: List[Dict[str, Any]]) -> List[str]:
        """
        Parse the Gemini response to extract suggested project IDs
        
        Args:
            response_text: The text response from Gemini
            all_projects: List of all projects to validate against
            
        Returns:
            List of suggested project IDs
        """
        print("DEBUG: Raw Gemini response:")
        print(response_text)
        
        try:
            import json
            import re
            
            # Create maps for name-based matching - MongoDB stores IDs as _id not id
            name_to_id = {project.get('name', '').lower(): str(project.get('_id')) for project in all_projects}
            print(f"DEBUG: Project name to ID mapping (sample): {list(name_to_id.items())[:5]}")
            
            # Debug full project structure
            if all_projects and len(all_projects) > 0:
                print(f"DEBUG: Example project document structure: {list(all_projects[0].keys())}")
            
            # Try to extract JSON from the response
            json_match = re.search(r'({[\s\S]*})', response_text)
            
            if json_match:
                json_str = json_match.group(1)
                print(f"DEBUG: Extracted JSON: {json_str}")
                
                try:
                    data = json.loads(json_str)
                    print(f"DEBUG: Parsed JSON data: {data}")
                    
                    # Extract suggested project names and convert to IDs
                    suggested_ids = []
                    
                    if "suggested_projects" in data and isinstance(data["suggested_projects"], list):
                        for suggestion in data["suggested_projects"]:
                            # Check for name field first
                            if "name" in suggestion:
                                project_name = suggestion["name"].lower()
                                if project_name in name_to_id:
                                    project_id = name_to_id[project_name]
                                    suggested_ids.append(project_id)
                                    print(f"DEBUG: Matched project by name: {project_name} -> {project_id}")
                                else:
                                    # Try fuzzy matching for slight name variations
                                    matched = False
                                    for name, id in name_to_id.items():
                                        if name in project_name or project_name in name:
                                            suggested_ids.append(id)
                                            print(f"DEBUG: Fuzzy matched project: {project_name} ~ {name} -> {id}")
                                            matched = True
                                            break
                                    
                                    if not matched:
                                        print(f"DEBUG: Could not match project name: {project_name}")
                            # Backward compatibility for id field
                            elif "id" in suggestion:
                                project_id_or_name = suggestion["id"]
                                # Check if it's actually a name
                                if project_id_or_name.lower() in name_to_id:
                                    project_id = name_to_id[project_id_or_name.lower()]
                                    suggested_ids.append(project_id)
                                    print(f"DEBUG: Matched name in id field: {project_id_or_name} -> {project_id}")
                    
                    if suggested_ids:
                        print(f"DEBUG: Found suggested projects from JSON: {suggested_ids}")
                        return suggested_ids
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON decode error: {str(e)}")
            
            # Fallback: Try to extract project names directly from the text
            print("DEBUG: Falling back to text-based extraction")
            suggested_ids = []
            
            # Search for project names in the text
            for project_name, project_id in name_to_id.items():
                if len(project_name) > 3 and project_name in response_text.lower():
                    suggested_ids.append(project_id)
                    print(f"DEBUG: Found project name in text: {project_name} -> {project_id}")
            
            # Return the matched projects (up to 5)
            if suggested_ids:
                print(f"DEBUG: Final suggested IDs from text matching: {suggested_ids[:5]}")
                return suggested_ids[:5]
            
            # Last resort - return first 3 projects if none matched
            if not suggested_ids and all_projects:
                first_three = [str(project.get('_id')) for project in all_projects[:3]]
                print(f"DEBUG: No matches found, returning first 3 projects: {first_three}")
                return first_three
                
            return []
                
        except Exception as e:
            print(f"ERROR parsing suggested projects: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return first 3 projects as fallback on error
            if all_projects:
                fallback = [str(project.get('_id')) for project in all_projects[:3]]
                print(f"DEBUG: Error occurred, using fallback: {fallback}")
                return fallback
            return []
    
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
