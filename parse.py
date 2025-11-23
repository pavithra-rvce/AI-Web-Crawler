import os
import openai
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env if present
load_dotenv()

# Configure OpenAI-compatible client for Groq
# Make sure .env has: GROQ_API_KEY=your_key_here
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
    rendered = prompt.format(
        dom_content=dom_content,
        parse_description=parse_description
    )
    return rendered


def call_groq_model(prompt: str, model_name: str) -> str:
    """
    Call Groq-hosted model using OpenAI-compatible client.
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a precise data extraction assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    return (response.choices[0].message.content or "").strip()


def parse_with_external_ai(dom_chunks, parse_description, model_name: str):
    """
    Uses Groq-hosted model to parse each DOM chunk.
    Returns combined text of all parsed chunks.
    """
    parsed_result = []

    for i, chunk in enumerate(dom_chunks, start=1):
        prompt = build_prompt(chunk, parse_description)
        result = call_groq_model(prompt, model_name)
        print(f"parsed batch {i} of {len(dom_chunks)}")
        parsed_result.append(result)

    return "\n".join(parsed_result)
