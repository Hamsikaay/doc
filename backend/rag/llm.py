# llm.py
"""
Small LLM wrapper. This is a placeholder that returns a deterministic answer.
Replace pseudo_llm_generate() with a call to OpenAI/Anthropic/HF inference endpoint.
"""
def pseudo_llm_generate(question: str, context: str) -> str:
    # Simple deterministic "answer" for demo.
    if not context:
        return "I couldn't find relevant context in the documents."
    return f"Answer (stub): For the question: {question}\n\nContext excerpt:\n{context[:400]}"

# Example real call (OpenAI pseudo)
# import openai
# def call_openai(prompt: str):
#     resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[...])
#     return resp.choices[0].message.content
