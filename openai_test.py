from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env from current folder
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

print("🔹 Checking if OPENAI_API_KEY is loaded...")
print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("🔹 Sending OpenAI test request...")
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Uji sambungan OpenAI: Siapa Nabi pertama dalam Islam?"}],
        max_completion_tokens=100
    )
    print("✅ OpenAI Response:\n", response.choices[0].message.content)
except Exception as e:
    print("❌ OpenAI Error:", e)
