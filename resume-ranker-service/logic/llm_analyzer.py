import os
import google.generativeai as genai
from typing import Optional


class LLMAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini LLM analyzer.
        
        Args:
            api_key: Gemini API key (if None, will try to get from environment)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def analyze_resume(self, resume_text: str, job_description: str) -> str:
        """
        Analyze resume against job description using Gemini LLM.
        
        Args:
            resume_text: Extracted resume text
            job_description: Job description text
            
        Returns:
            HR-style analysis as string
        """
        prompt = f"""As an HR professional, analyze the following resume against the job description.
        
Job Description:
{job_description}

Resume:
{resume_text}

Please provide a comprehensive HR-style analysis including:
1. Overall match assessment
2. Key strengths
3. Potential gaps or concerns
4. Recommendations

Be professional and constructive in your analysis."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise ValueError(f"Error generating LLM analysis: {str(e)}")

