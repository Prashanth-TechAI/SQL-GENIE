import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

def get_llm():
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_API_KEY not found in environment")
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key
    )

humanize_prompt = PromptTemplate(
    input_variables=["analysis", "context"],
    template="""
You are a helpful assistant that explains analytical results to non-technical users in the simple concise , human understandable manner .

Dataset context: {context}
Raw result: {analysis}

Rewrite the result in a accurate, short, concise,  simple, clear, and human-like explanation.
"""
)

def humanize_answer(analysis: str, context: str = "") -> str:
    chain = LLMChain(llm=get_llm(), prompt=humanize_prompt)
    return chain.run({"analysis": analysis, "context": context}).strip()
