import streamlit as st
import pandas as pd
from llm_utils import (
    generate_questions,
    generate_questions_from_categories,
    generate_answer,
    extract_text_from_file
)

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Islamic LLM Dataset Generator", layout="wide")
st.title("🕌 Islamic LLM Dataset Generator")

# ---------------------- MODEL STATUS ----------------------
def show_model_status(model_name: str):
    """
    Display which model handled the generation (OpenAI, HuggingFace, or Mistral API).
    """
    status_map = {
        "OpenAI": "💡 Using OpenAI GPT-3.5 (primary)",
        "HuggingFace": "⚙️ Using HuggingFace Mistral (fallback)",
        "Mistral API": "🚀 Using Mistral API (final fallback)"
    }
    if model_name in status_map:
        st.info(status_map[model_name])

# ---------------------- COST ESTIMATOR ----------------------
def estimate_openai_cost(num_questions, avg_tokens_per_response=500):
    """
    Rough cost estimation based on GPT-3.5 pricing ($0.0005 / 1K input tokens, $0.0015 / 1K output tokens)
    """
    input_cost_per_1k = 0.0005
    output_cost_per_1k = 0.0015
    total_tokens = num_questions * avg_tokens_per_response
    estimated_cost = (total_tokens / 1000) * (input_cost_per_1k + output_cost_per_1k)
    return round(estimated_cost, 4)

# ---------------------- SIDEBAR ----------------------
st.sidebar.header("📚 Category Hierarchy")

use_reference_file = st.sidebar.checkbox(
    "Use reference document for question generation", value=True
)

num_questions = st.sidebar.number_input(
    "Number of Questions to Generate",
    min_value=1, max_value=50, value=30, step=1,
    help="Set how many questions you want to generate for this category hierarchy."
)

# Estimated cost preview
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Estimated Cost (OpenAI)")
estimated_cost = estimate_openai_cost(num_questions)
st.sidebar.write(f"Approx. **${estimated_cost} USD** for {num_questions} Q&A pairs.")
st.sidebar.caption("💡 Actual cost may vary depending on token length.")

categories = {}
categories['Tahap 1: Keupayaan Teras'] = st.sidebar.text_input("Tahap 1: Keupayaan Teras (Level 1)", key="cat_1")
categories['Tahap 2: Domain'] = st.sidebar.text_input("Tahap 2: Domain (Level 2)", key="cat_2")
categories['Tahap 3: Tema'] = st.sidebar.text_input("Tahap 3: Tema (Level 3)", key="cat_3")
categories['Tahap 4: Senario/Entiti Tertentu'] = st.sidebar.text_input("Tahap 4: Senario/Entiti Tertentu (Level 4)", key="cat_4")

# Difficulty
difficulty_options = {
    "Simple": "Provide a long, detailed answer with direct explanations.",
    "Medium": "Provide a long, detailed answer considering multiple scenarios.",
    "Complex": "Provide a long, detailed answer with a clear reasoning process, step-by-step."
}
categories['Difficulty'] = st.sidebar.selectbox(
    "Difficulty (Level 5)",
    options=list(difficulty_options.keys()),
    help="Simple: direct facts | Medium: mixed conditions | Complex: reasoning cases"
)

# Strategi
categories['Strategi'] = st.sidebar.text_input("Strategi (Level 6)", key="cat_6")

# Jenis Data
jenis_data_options = [
    "Penafian keselamatan",
    "Pengesanan serangan berat sebelah",
    "Perbincangan ilmu budaya",
    "Pengesanan maklumat palsu",
    "Bimbingan nilai positif",
    "Pemahaman dasar dan system",
    "Penerangan neutral dan objektif"
]
categories['Jenis Data'] = st.sidebar.selectbox(
    "Jenis Data (Level 7)",
    options=jenis_data_options
)

# ---------------------- DOCUMENT UPLOAD ----------------------
st.header("📤 Document Upload")
uploaded_file = st.file_uploader(
    "Upload a document (PDF, DOCX, TXT, XLSX)",
    type=['pdf', 'docx', 'txt', 'xlsx']
)

document_text = ""
if uploaded_file is not None:
    st.success("✅ Document uploaded successfully!")

    with st.spinner("Extracting text from document..."):
        if uploaded_file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            document_text = df.to_string()
        else:
            document_text = extract_text_from_file(uploaded_file)

    st.text_area("📄 Document Preview (first 1000 characters):", document_text[:1000], height=200)

# ---------------------- VALIDATION ----------------------
if not all(categories.values()):
    st.warning("⚠️ Please fill in all 7 category levels before proceeding.")
else:
    st.success("✅ All categories defined!")

    # ---------------------- QUESTION GENERATION ----------------------
    if st.button("✨ Generate Questions"):
        with st.spinner("Generating questions..."):
            try:
                show_model_status("OpenAI")
                if use_reference_file and uploaded_file is not None:
                    questions = generate_questions(document_text, categories, num_questions=int(num_questions))
                else:
                    questions = generate_questions_from_categories(categories, num_questions=int(num_questions))
            except Exception:
                show_model_status("HuggingFace")
                try:
                    if use_reference_file and uploaded_file is not None:
                        questions = generate_questions(document_text, categories, num_questions=int(num_questions))
                    else:
                        questions = generate_questions_from_categories(categories, num_questions=int(num_questions))
                except Exception:
                    show_model_status("Mistral API")
                    st.error("All models failed. Please check your API keys and network connection.")
                    questions = []

        st.session_state.questions = questions
        if questions:
            st.success(f"✅ Generated {len(questions)} questions!")

    # ---------------------- ANSWER GENERATION ----------------------
    if 'questions' in st.session_state:
        st.header("💬 Generated Questions and Answers")

        if st.button("🧠 Generate Answers for All Questions"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            qa_pairs = []
            total_q = len(st.session_state.questions)

            for i, question in enumerate(st.session_state.questions):
                status_text.text(f"Generating answer for question {i+1}/{total_q}")
                progress_bar.progress((i+1) / total_q)

                try:
                    show_model_status("OpenAI")
                    answer = generate_answer(question, document_text, categories)
                except Exception:
                    show_model_status("HuggingFace")
                    try:
                        answer = generate_answer(question, document_text, categories)
                    except Exception:
                        show_model_status("Mistral API")
                        answer = "Model failed to respond."

                qa = {'Question': question, 'Answer': answer, **categories}
                qa['Source'] = document_text if use_reference_file else ""
                qa_pairs.append(qa)

            progress_bar.progress(1.0)
            status_text.text("✅ All answers generated!")

            # 💰 Cost estimation for answers
            estimated_total_cost = estimate_openai_cost(total_q, avg_tokens_per_response=700)
            st.success(f"💰 Estimated OpenAI usage cost: **${estimated_total_cost} USD**")

            st.session_state.qa_pairs = qa_pairs
            st.session_state.answers = [qa['Answer'] for qa in qa_pairs]

        # ---------------------- DISPLAY RESULTS ----------------------
        if 'qa_pairs' in st.session_state:
            for i, qa in enumerate(st.session_state.qa_pairs):
                with st.expander(f"📘 Q&A Pair {i+1}"):
                    st.markdown(f"**Question:** {qa['Question']}")
                    st.markdown(f"**Answer:**\n{qa['Answer']}")

    # ---------------------- EXPORT ----------------------
    if 'questions' in st.session_state and 'answers' in st.session_state:
        st.divider()
        st.subheader("📦 Export Dataset")

        source_text = document_text if use_reference_file else ""
        df = pd.DataFrame({
            "Question": st.session_state.questions,
            "Answer": st.session_state.answers,
            "Source": [source_text] * len(st.session_state.questions)
        })

        st.download_button(
            label="📥 Download Q&A Dataset (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="islamic_llm_dataset.csv",
            mime="text/csv"
        )

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit + OpenAI + HuggingFace + Mistral API.")

if use_reference_file and uploaded_file is None:
    st.info("Please upload a document to get started.")
