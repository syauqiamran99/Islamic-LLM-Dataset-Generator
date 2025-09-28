from huggingface_hub import InferenceClient, login
from transformers import pipeline
from dotenv import load_dotenv
import os

# Load env
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
hf_api_key = os.getenv("HF_API_KEY")

# Initialize Mistral API client
mistral_client = None
if hf_api_key:
    mistral_client = InferenceClient(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        token=hf_api_key
    )

# Try HuggingFace pipeline
try:
    hf_pipe = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2")
except:
    hf_pipe = None

prompt = "Apakah maksud Rukun Iman dalam Islam?"
print("🔹 Sending request...\n")

try:
    if openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Anda ialah pembantu Islam dalam Bahasa Melayu."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=200
        )
        print("✅ OpenAI response:\n", response.choices[0].message.content)
    elif hf_pipe:
        print("✅ HuggingFace pipeline response:\n")
        result = hf_pipe(prompt, max_length=200, do_sample=True, temperature=0.7)
        print(result[0]['generated_text'])
    elif mistral_client:
        print("✅ Mistral API response:\n")
        result = mistral_client.text_generation(prompt, max_new_tokens=150, temperature=0.7)
        print(result)
    else:
        print("⚠️ No model available.")
except Exception as e:
    print("❌ Error:", e)