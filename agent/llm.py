import os
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables (like GROQ_API_KEY)
load_dotenv()

def get_llm() -> BaseChatModel:
    """
    Get the primary LLM for decision making and extraction.
    Requires GROQ_API_KEY to be set in the environment or a .env file.
    """
    if "GROQ_API_KEY" not in os.environ:
        print("WARNING: GROQ_API_KEY not found in environment. LLM calls will fail.")
        # Using a dummy fallback string just so it doesn't crash on import/instantiation, 
        # though API calls will fail if it's invalid.
        os.environ["GROQ_API_KEY"] = "mock_key_for_testing"

    return ChatGroq(model="openai/gpt-oss-120b", temperature=0)
