# Islamic LLM Dataset Generator

This project is a Streamlit web app for generating Islamic knowledge question-answer datasets using OpenAI's GPT models.  
It supports hierarchical category input, reference document upload, and strict control over question types via "Jenis Data".

## Features

- **Category Hierarchy:** Define up to 7 levels, including Difficulty, Strategi, and Jenis Data.
- **Jenis Data Control:** Generate questions and answers that strictly follow selected data types (e.g., safety disclaimer, positive values, neutral/objective, etc.).
- **Reference Document:** Optionally upload PDF, DOCX, TXT, or XLSX files to use as context for question generation.
- **Malay Language:** All questions and answers are generated in Bahasa Melayu.
- **Customizable Output:** Download generated Q&A pairs as a CSV file, including all category metadata and source document text.

## Libraries Used

- [streamlit](https://streamlit.io/) — Web app framework
- [openai](https://github.com/openai/openai-python) — OpenAI API client
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment variable management
- [pandas](https://pandas.pydata.org/) — Data manipulation and CSV export
- [PyPDF2](https://pypi.org/project/PyPDF2/) — PDF text extraction
- [python-docx](https://python-docx.readthedocs.io/) — DOCX text extraction

## Getting Started

### 1. Clone the repository

```sh
git clone <your-repo-url>
cd islamic_llm_dataset
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY="sk-..."
```

### 4. Run the app

```sh
streamlit run app.py
```

## Usage

1. **Set Category Hierarchy:** Fill in all category levels in the sidebar.
2. **Select Jenis Data:** Choose the type of question/answer behavior required.
3. **Upload Reference Document (optional):** If enabled, upload a document for context.
4. **Set Number of Questions:** Choose how many questions to generate.
5. **Generate Questions:** Click the button to generate questions.
6. **Generate Answers:** Click to generate answers for all questions.
7. **Download Dataset:** Export the results as a CSV file.

## Supported Jenis Data

- Penafian keselamatan
- Pengesanan serangan berat sebelah
- Perbincangan ilmu budaya
- Pengesanan maklumat palsu
- Bimbingan nilai positif
- Pemahaman dasar dan system
- Penerangan neutral dan objektif

## File Structure

- `app.py` — Main Streamlit app
- `llm_utils.py` — LLM interaction and utility functions
- `.env` — API key configuration
- `requirements.txt` — Python dependencies

## License

MIT License

---

**Developed for Islamic knowledge dataset creation using LLMs.**
