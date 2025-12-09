# # llm.py
# """
# Small LLM wrapper. This is a placeholder that returns a deterministic answer.
# Replace pseudo_llm_generate() with a call to OpenAI/Anthropic/HF inference endpoint.
# """
# def pseudo_llm_generate(question: str, context: str) -> str:
#     # Simple deterministic "answer" for demo.
#     if not context:
#         return "I couldn't find relevant context in the documents."
#     return f"Answer (stub): For the question: {question}\n\nContext excerpt:\n{context[:400]}"

# # Example real call (OpenAI pseudo)
# # import openai
# # def call_openai(prompt: str):
# #     resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[...])
# #     return resp.choices[0].message.content

# llm.py
# import os
# import requests
# from dotenv import load_dotenv
# load_dotenv()

# HF_API_KEY = os.getenv("HF_API_KEY")


# LLM_MODEL = "google/gemma-2-2b-it"
# API_URL = "https://router.huggingface.co/v1/chat/completions" 


# HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# def generate_answer(question, context):
#     prompt = f"""
# You are a helpful AI assistant. Use ONLY the context below to answer the question.

# Context:
# {context}

# Question: {question}

# Answer:
# """

#     response = requests.post(
#         API_URL,
#         headers=HEADERS,
#         json={"inputs": prompt},
#     )

#     if response.status_code != 200:
#         raise Exception(f"HF LLM API Error: {response.text}")

#     # HF returns a list of dicts
#     generated = response.json()[0]["generated_text"]
#     return generated[len(prompt):].strip()

# import os
# from dotenv import load_dotenv
# from huggingface_hub import InferenceClient

# load_dotenv()

# HF_TOKEN = os.getenv("HF_TOKEN")

# # ⭐ Best LLM for RAG
# LLM_MODEL = "Qwen/Qwen2.5-72B-Instruct"

# client = InferenceClient(
#     provider="hf-inference",
#     api_key=HF_TOKEN,
# )

# def generate_answer(question: str, context: str) -> str:
#     """
#     Sends the RAG prompt to HuggingFace Inference API LLM.
#     """
#     prompt = f"""
#     You are a helpful AI assistant. Answer using ONLY the context provided.
#     If the answer is not in the context, say: "The answer is not in the document."

#     Context:
#     {context}

#     Question:
#     {question}

#     Answer:
#     """

#     response = client.chat.completions.create(
#         model=LLM_MODEL,
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=512,
#         temperature=0.1  # low temp = less hallucination
#     )

#     return response.choices[0].message["content"]
# 

import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")

# ✅ THIS MODEL IS CONFIRMED WORKING FOR YOU
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
