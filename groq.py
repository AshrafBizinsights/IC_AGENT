import requests
import os

headers = {
    "Authorization": f"Bearer {os.getenv('LITELLM_API_KEY')}",
    "Content-Type": "application/json"
}
data = {
    "model": "llama3-8b-8192",
    "messages": [{"role": "user", "content": "Hello from Groq"}]
}

response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
print(response.status_code, response.text)