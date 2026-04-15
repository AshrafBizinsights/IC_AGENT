import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

try:
    response = client.embeddings.create(
        input="Hello, how are you?",
        model="text-embedding-3-small"
    )
    vector = response.data[0].embedding
    print("✅ OpenAI embedding is working!")
    print("Vector length:", len(vector))
    print("First 5 values:", vector[:5])
except Exception as e:
    print("❌ Failed to get embedding.")
    print("Error:", e)
