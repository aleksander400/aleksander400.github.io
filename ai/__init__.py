# Moduł integracji AI - podstawowa konfiguracja
import openai

def setup_openai(api_key):
    openai.api_key = api_key
    print("OpenAI API zostało skonfigurowane.")

def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']
