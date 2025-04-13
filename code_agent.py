import openai

def generate_code(prompt):
    """Generate code based on natural language prompt"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "user", 
                "content": f"Napisz kod dla: {prompt}"
            }],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Błąd generowania kodu]: {e}"
