import os
from langchain_groq.chat_models import ChatGroq

def get_llm():
    key = os.getenv("LLM_API_KEY")
    if not key:
        raise RuntimeError("LLM_API_KEY environment variable is not set")
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=key
    )
