import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Make sure .env is loaded

API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
headers = {
    "Authorization": f"Bearer {os.environ.get('HUGGINGFACEHUB_API_TOKEN')}"
}

data = {
    "inputs": "Hello, how are you?"
}

response = requests.post(API_URL, headers=headers, json=data)

if response.status_code == 200:
    print("✅ Hugging Face API is working!")
    print("Vector output:", response.json()[0][:5], "...")  # show first 5 dims
else:
    print("❌ Error")
    print("Status code:", response.status_code)
    print("Response:", response.text)
