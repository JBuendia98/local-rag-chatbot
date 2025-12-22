# app/rag/prompt.py

from typing import List

def build_rag_prompt(context: List[str], question: str) -> str:
    """
    Builds a grounded prompt for the LLM using retrieved context.
    """

    context_text = "\n\n".join(context)

    return f"""You are a helpful assistant.

Answer the question using ONLY the context below.
If the answer cannot be found in the context, say "I don't know".

Context:
{context_text}

Question:
{question}

Answer:
"""
