import os
import openai
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import re

# Load environment variables from .env if present
load_dotenv()

# Configure OpenAI-compatible client for Groq
client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)


def build_prompt(dom_content: str, parse_description: str) -> str:
    """
    Render the prompt from the template using LangChain's ChatPromptTemplate.
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # Clean the content before sending to AI
    cleaned_content = clean_content_for_ai(dom_content)
    
    rendered = prompt.format(
        dom_content=cleaned_content,
        parse_description=parse_description
    )
    return rendered


def clean_content_for_ai(content: str, max_length: int = 12000) -> str:
    """
    Clean and prepare content for AI processing
    """
    if not content:
        return "No content available"
    
    # Remove binary/encoded characters
    cleaned = re.sub(r'[^\x20-\x7E\n\t]', '', content)
    
    # Remove extra whitespace but preserve structure
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Limit length to avoid token limits
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "... [content truncated]"
    
    return cleaned.strip()


def call_groq_model(prompt: str, model_name: str) -> str:
    """
    Call Groq-hosted model using OpenAI-compatible client.
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Return only the requested data, no explanations."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=2000
        )
        result = (response.choices[0].message.content or "").strip()
        
        # Validate the response
        if is_garbled_response(result):
            return "❌ Unable to extract information. The website content may not contain relevant data or may be in an unsupported format."
        
        return result
        
    except Exception as e:
        return f"❌ Error calling AI model: {str(e)}"


def is_garbled_response(text: str) -> bool:
    """
    Check if the AI response is garbled/encoded
    """
    if not text:
        return True
    
    # Check for excessive special characters or repeated patterns
    if len(text) < 50:  # Too short to be meaningful
        return True
    
    # Check for common garbled patterns
    garbled_indicators = [
        r'�',  # Replacement character
        r'\.\.\.',  # Excessive dots
        r'\x00',  # Null bytes
    ]
    
    for pattern in garbled_indicators:
        if re.search(pattern, text):
            return True
    
    # Check if text is mostly non-alphanumeric
    alphanumeric_ratio = len(re.findall(r'[a-zA-Z0-9]', text)) / len(text)
    if alphanumeric_ratio < 0.3:  # Less than 30% alphanumeric
        return True
    
    return False


def parse_with_external_ai(dom_chunks, parse_description, model_name: str):
    """
    Uses Groq-hosted model to parse each DOM chunk.
    Returns combined text of all parsed chunks.
    """
    parsed_result = []

    for i, chunk in enumerate(dom_chunks, start=1):
        print(f"Processing batch {i} of {len(dom_chunks)}")
        
        prompt = build_prompt(chunk, parse_description)
        result = call_groq_model(prompt, model_name)
        
        # Skip empty or error results
        if result and not result.startswith("❌"):
            parsed_result.append(result)
        else:
            print(f"Batch {i} failed or returned no data")
    
    if not parsed_result:
        return "❌ No relevant information could be extracted from the website content. The site may not contain information about Solution Engineer positions, or the content format may not be compatible."
    
    return "\n\n".join(parsed_result)
