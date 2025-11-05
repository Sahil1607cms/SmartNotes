import os
import json
from typing import List, Dict, Optional
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
    
    def __init__(self, api_key: str = os.getenv("GROQ_API_KEY"), model: str = "llama3-8b-8192"):
        """
        Initialize the TextSummarizer.
        
        Args:
            api_key (str): Groq API key. If None, will try to get from environment variable.
            model (str): The Groq model to use for summarization.
        """
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        
    def create_prompt_template(self, style: str = "general") -> str:
        """
        Create different prompt templates for various summarization styles.
        
        Args:
            style (str): The style of summary ('general', 'bullet_points', 'executive', 'detailed')
            
        Returns:
            str: Prompt template string
        """
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
    
    def preprocess_transcript(self, transcript: List[str]) -> str:
        """
        Preprocess transcript list into a single string.
        
        Args:
            transcript (List[str]): List of transcript segments
            
        Returns:
            str: Processed transcript as a single string
        """
        if isinstance(transcript, list):
            # Join list elements, assuming each element is a sentence or paragraph
            processed_text = " ".join(transcript)
        elif isinstance(transcript, str):
            processed_text = transcript
        else:
            raise ValueError("Transcript must be a string or list of strings")
        
        # Clean up extra whitespace
        processed_text = " ".join(processed_text.split())
        
        return processed_text
    
    def generate_summary(self, 
                        transcript: List[str] | str, 
                        prompt_template: str = None,
                        style: str = "general",
                        custom_instructions: str = None,
                        max_tokens: int = 1024,
                        temperature: float = 0.7) -> Dict[str, any]:
        """
        Generate a summary of the transcript using Groq API.
        
        Args:
            transcript (List[str] | str): The transcript to summarize
            prompt_template (str): Custom prompt template. If None, uses style-based template
            style (str): Predefined style for summarization
            custom_instructions (str): Custom instructions for 'custom' style
            max_tokens (int): Maximum tokens for the response
            temperature (float): Temperature for response generation
            
        Returns:
            Dict: Dictionary containing summary, metadata, and status
        """
        try:
            # Preprocess transcript
            processed_transcript = self.preprocess_transcript(transcript)
            
            # Validate transcript length (basic check)
            if len(processed_transcript.strip()) == 0:
                return {
                    "status": "error",
                    "error": "Empty transcript provided",
                    "summary": None
                }
            
            # Create prompt
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
                # Use provided custom prompt template
                final_prompt = prompt_template.format(transcript=processed_transcript)
            
            logger.info(f"Generating summary using model: {self.model}")
            
            # Make API call to Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": final_prompt,
                    }
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            # Extract summary
            summary = chat_completion.choices[0].message.content
            
            return {
                "status": "success",
                "summary": summary,
                "metadata": {
                    "model": self.model,
                    "style": style,
                    "transcript_length": len(processed_transcript),
                    "summary_length": len(summary),
                    "tokens_used": chat_completion.usage.total_tokens if hasattr(chat_completion, 'usage') else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "summary": None
            }

def summarize_transcript(transcript: List[str] | str, 
                        prompt: str = None,
                        api_key: str = os.getenv("GROQ_API_KEY"),
                        style: str = "general",
                        model: str = "llama3-8b-8192") -> str:
    """
    Main function to summarize transcript - simplified interface.
    
    Args:
        transcript (List[str] | str): The transcript to summarize
        prompt (str): Custom prompt template (optional)
        api_key (str): Groq API key (optional, can use env variable)
        style (str): Summary style if no custom prompt provided
        model (str): Groq model to use
        
    Returns:
        str: Generated summary
    """
    try:
        summarizer = TextSummarizer(api_key=os.getenv("GROQ_API_KEY"), model=model)
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

# Example usage and testing
if __name__ == "__main__":
    # Example transcript
    sample_transcript = [
        "Hello everyone, welcome to today's team meeting.",
        "We're here to discuss the Q4 project timeline and deliverables.",
        "First, let's review what we accomplished last quarter.",
        "We successfully launched the new mobile app feature.",
        "User engagement increased by 25% after the launch.",
        "Moving forward, we need to focus on the backend optimization.",
        "The deadline for this is December 15th.",
        "Sarah will lead the database migration.",
        "Mike will handle the API improvements.",
        "Let's schedule weekly check-ins to track progress.",
        "Any questions or concerns about the timeline?"
    ]
    
    # Custom prompt template example
    custom_prompt = """
    Analyze the following transcript and provide:
    1. A brief overview
    2. Key action items
    3. Important dates mentioned
    
    Transcript: {transcript}
    
    Analysis:
    """
    
    # Example 1: Using the main function with default style
    print("=== Example 1: General Summary ===")
    summary1 = summarize_transcript(sample_transcript)
    print(summary1)
    print("\n")
    
    # Example 2: Using custom prompt
    print("=== Example 2: Custom Prompt ===")
    summary2 = summarize_transcript(sample_transcript, prompt=custom_prompt)
    print(summary2)
    print("\n")
    
    # Example 3: Using the class directly for more control
    print("=== Example 3: Using Class Directly ===")
    try:
        summarizer = TextSummarizer()  # Will use GROQ_API_KEY from environment
        result = summarizer.generate_summary(
            transcript=sample_transcript,
            style="executive",
            temperature=0.5
        )
        
        if result["status"] == "success":
            print("Summary:", result["summary"])
            print("Metadata:", json.dumps(result["metadata"], indent=2))
        else:
            print("Error:", result["error"])
            
    except Exception as e:
        print(f"Please set your GROQ_API_KEY environment variable: {e}")