import os
import json
from typing import List, Dict, Optional, Any
from groq import Groq
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextSummarizer:
    """
    A text summarizer class that uses Groq API to generate summaries
    of transcripts based on customizable prompt templates.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama3-8b-8192"):
        """
        Initialize the TextSummarizer.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        
    def create_prompt_template(self, style: str = "general") -> str:
        templates = {
            "general": """
Please provide a concise summary of the following transcript. Focus on the main points and key information:

Transcript:
{transcript}

Summary:
""",
            
            "bullet_points": """
Please summarize the following transcript in bullet point format, highlighting the key points:

Transcript:
{transcript}

Key Points:
• 
""",
            
            "executive": """
Please provide an executive summary of the following transcript suitable for business stakeholders. Include:
- Main topic/purpose
- Key decisions or outcomes
- Action items (if any)

Transcript:
{transcript}

Executive Summary:
""",
            
            "detailed": """
Please provide a detailed summary of the following transcript that includes:
1. Main themes and topics discussed
2. Important details and context
3. Key takeaways or conclusions

Transcript:
{transcript}

Detailed Summary:
""",
            
            "custom": """
{custom_instructions}

Transcript:
{transcript}

Summary:
"""
        }
        
        return templates.get(style, templates["general"])
    
    def preprocess_transcript(self, transcript: List[str] | str) -> str:
        if isinstance(transcript, list):
            processed_text = " ".join(transcript)
        elif isinstance(transcript, str):
            processed_text = transcript
        else:
            raise ValueError("Transcript must be a string or list of strings")
        
        processed_text = " ".join(processed_text.split())
        return processed_text
    
    def generate_summary(self, 
                        transcript: List[str] | str, 
                        prompt_template: Optional[str] = None,
                        style: str = "general",
                        custom_instructions: Optional[str] = None,
                        max_tokens: int = 1024,
                        temperature: float = 0.7
                        ) -> Dict[str, Any]:
        """
        Generate summary using Groq API.
        """

        try:
            processed_transcript = self.preprocess_transcript(transcript)
            
            if len(processed_transcript.strip()) == 0:
                return {
                    "status": "error",
                    "error": "Empty transcript provided",
                    "summary": None
                }
            
            # build prompt
            if prompt_template is None:
                if style == "custom" and custom_instructions:
                    prompt_template = self.create_prompt_template("custom")
                    final_prompt = prompt_template.format(
                        transcript=processed_transcript,
                        custom_instructions=custom_instructions
                    )
                else:
                    prompt_template = self.create_prompt_template(style)
                    final_prompt = prompt_template.format(transcript=processed_transcript)
            else:
                final_prompt = prompt_template.format(transcript=processed_transcript)
            
            logger.info(f"Generating summary using model: {self.model}")
            
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": final_prompt}],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            summary = chat_completion.choices[0].message.content
            
            return {
                "status": "success",
                "summary": summary,
                "metadata": {
                    "model": self.model,
                    "style": style,
                    "transcript_length": len(processed_transcript),
                    "summary_length": len(summary) if summary else 0,
                    "tokens_used": getattr(chat_completion.usage, "total_tokens", None)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {"status": "error", "error": str(e), "summary": None}


def summarize_transcript(
    transcript: List[str] | str, 
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    style: str = "general",
    model: str = "llama3-8b-8192"
) -> str:
    try:
        summarizer = TextSummarizer(api_key=api_key or os.getenv("GROQ_API_KEY"), model=model)
        
        result = summarizer.generate_summary(
            transcript=transcript,
            prompt_template=prompt,
            style=style
        )
        
        if result["status"] == "success":
            return result["summary"]
        else:
            return f"Error: {result['error']}"
            
    except Exception as e:
        return f"Error initializing summarizer: {str(e)}"


# Example usage
if __name__ == "__main__":
    sample_transcript = [
        "Hello everyone, welcome to today's team meeting.",
        "We're here to discuss the Q4 project timeline and deliverables."
    ]
    
    print("=== Example ===")
    print(summarize_transcript(sample_transcript))
