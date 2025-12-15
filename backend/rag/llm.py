import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")


MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

client = InferenceClient(
    model=MODEL_ID,
    token=HF_TOKEN
)

def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a professional teacher AI.

STRICT RULES:
- Always format the answer using:
  - Headings
  - Bullet points
  - Numbered lists
- Add proper line breaks.
- Never return a single paragraph.
- Make answers exam-ready.

Context:
{context}

Question:
{question}

Now return a clean, well-structured formatted answer.
"""

    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600,
        temperature=0.3,
    )

    return response.choices[0].message["content"]
