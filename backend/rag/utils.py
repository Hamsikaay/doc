import hashlib

def question_to_key(question: str) -> str:
    clean = question.strip().lower()
    return "qa:" + hashlib.sha256(clean.encode()).hexdigest()
