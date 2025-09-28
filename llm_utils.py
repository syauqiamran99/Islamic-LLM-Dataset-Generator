import os
import io
import openai
from dotenv import load_dotenv
from typing import List, Dict
from huggingface_hub import login, InferenceClient
import PyPDF2
import docx

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

openai_api_key = os.getenv("OPENAI_API_KEY")
hf_token = os.getenv("HF_API_KEY")

# ---------------------------------------------------------------------
# Initialize OpenAI client (Primary)
# ---------------------------------------------------------------------
if openai_api_key:
    client = openai.OpenAI(api_key=openai_api_key)
    print("✅ OpenAI client initialized.")
else:
    client = None
    print("⚠️ OPENAI_API_KEY missing — OpenAI disabled.")

# ---------------------------------------------------------------------
# Initialize Hugging Face Cloud (Mistral)
# ---------------------------------------------------------------------
if hf_token:
    try:
        login(hf_token)
        print("✅ Logged into HuggingFace successfully.")
    except Exception as e:
        print(f"⚠️ HuggingFace login failed: {e}")

    try:
        mistral_client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=hf_token
        )
        print("✅ Mistral Cloud API client initialized.")
    except Exception as e:
        mistral_client = None
        print("⚠️ Failed to connect to Mistral Cloud API:", e)
else:
    mistral_client = None
    print("⚠️ HF_API_KEY not found in .env, skipping Mistral setup.")

# ---------------------------------------------------------------------
# Helper function — Try model hierarchy
# ---------------------------------------------------------------------
def _try_generate(prompt: str, max_tokens: int = 300) -> str:
    """
    Smart fallback system:
      1. Try OpenAI GPT-3.5
      2. Fallback to Mistral Cloud (Hugging Face API)
    """
    # 1️⃣ Try OpenAI first
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Anda ialah pembantu yang menjawab soalan Islam dalam Bahasa Melayu."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=max_tokens
            )
            print("✅ OpenAI response successful.")
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("⚠️ OpenAI failed:", e)

    # 2️⃣ Fallback to Mistral Cloud
    if mistral_client:
        try:
            mistral_output = mistral_client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.7
            )
            print("✅ Mistral Cloud response successful.")
            return mistral_output.strip()
        except Exception as e:
            print("⚠️ Mistral Cloud failed:", e)

    # ❌ No model worked
    return "⚠️ No model available"

# ---------------------------------------------------------------------
# Generate Questions from Document
# ---------------------------------------------------------------------
def generate_questions(document_text: str, categories: Dict[str, str], num_questions: int = 10) -> List[str]:
    category_str = ", ".join([f"{k}: {v}" for k, v in categories.items()])
    prompt = f"""
    Berdasarkan dokumen berikut dan kategori: {category_str},
    jana {num_questions} soalan dalam Bahasa Melayu.

    Dokumen:
    {document_text[:1500]}
    """

    result = _try_generate(prompt)
    return [q.strip() for q in result.split("\n") if q.strip()][:num_questions]

# ---------------------------------------------------------------------
# Generate Questions (Category only)
# ---------------------------------------------------------------------
def generate_questions_from_categories(categories: Dict[str, str], num_questions: int = 10) -> List[str]:
    category_str = ", ".join([f"{k}: {v}" for k, v in categories.items()])
    prompt = f"""
    Berdasarkan hierarki kategori Islam berikut:
    {category_str}

    Jana {num_questions} soalan yang sesuai dalam Bahasa Melayu.
    """
    result = _try_generate(prompt)
    return [q.strip() for q in result.split("\n") if q.strip()][:num_questions]

# ---------------------------------------------------------------------
# Generate Answers
# ---------------------------------------------------------------------
def generate_answer(question: str, document_text: str, categories: Dict[str, str]) -> str:
    category_str = ", ".join([f"{k}: {v}" for k, v in categories.items()])
    prompt = (
        f"Kategori: {category_str}\n"
        f"Dokumen: {document_text[:1500]}\n"
        f"Soalan: {question}\n"
        "Jawab dalam Bahasa Melayu dengan jelas, sopan, dan sertakan penjelasan ringkas."
    )

    return _try_generate(prompt, max_tokens=400)

# ---------------------------------------------------------------------
# Extract Text from File
# ---------------------------------------------------------------------
def extract_text_from_file(file) -> str:
    """Extract text from PDF, DOCX, or TXT files."""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        return "".join([page.extract_text() for page in reader.pages])

    elif file.name.endswith(".docx"):
        doc = docx.Document(io.BytesIO(file.read()))
        return "\n".join([para.text for para in doc.paragraphs])

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")