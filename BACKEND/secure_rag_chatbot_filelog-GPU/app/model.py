import ollama

def generate_answer(question, context):
    prompt = f"Use the following context to answer:\\n\\n{context}\\n\\nQuestion: {question}"
    response = ollama.chat(model="qwen3:8b", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]