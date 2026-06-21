# HealthBot

A retrieval-augmented chatbot that answers diet, fitness, and general health questions for college students. Responses are grounded in public health guidelines from WHO, ICMR-NIN, and ACSM, with Gemini 2.5 Flash handling generation.

## Overview

General-purpose chatbots will readily answer fitness and nutrition questions, but they rarely cite anything and can drift into confidently incorrect territory. This project retrieves relevant passages from a curated set of public health documents before generating a response, so answers stay traceable to a real source where possible. For questions outside the scope of those documents — such as "how many pushups should a beginner do" — it falls back on general exercise-science reasoning rather than refusing to answer.

## How It Works

The project is split into two stages.

**Ingestion** (`ingest.py`) loads the PDFs in `data/` using `PyMuPDFLoader`, splits them into ~1000-character chunks with 200 characters of overlap, embeds them locally using `sentence-transformers/all-MiniLM-L6-v2`, and writes the result to a FAISS index in `faiss_db/`. This runs once, and again any time the source documents change.

**Serving** (`app.py`) is the Streamlit application. On startup it loads the prebuilt FAISS index rather than rebuilding it, retrieves the top 6 relevant chunks for each query, and passes them along with conversation history into a LangChain chain (`RunnableParallel → prompt → LLM → StrOutputParser`). Responses stream back token by token via `st.write_stream()`.

Conversation memory is handled manually: each turn rebuilds the `HumanMessage`/`AIMessage` history and passes it through a `MessagesPlaceholder` in the prompt template.

## Project Structure

```
.
├── app.py                    Streamlit app — loads the FAISS index, runs the RAG chain, handles chat UI
├── ingest.py                  Builds the FAISS index from source PDFs
├── style.css                   Custom UI styling, loaded via load_css()
├── data/                       Source PDFs used for retrieval
├── faiss_db/                    Generated vector index (output of ingest.py)
├── .streamlit/secrets.toml       API keys (not committed)
└── requirements.txt
```

## Sources

- WHO Physical Activity Guidelines
- WHO guidance on depressive disorders and mental health
- ICMR-NIN Dietary Guidelines for Indians
- ACSM Exercise Testing and Prescription Guidelines

These PDFs are included in `data/` for development transparency. Anyone extending this beyond a personal or academic project should check redistribution terms on the original publications before shipping the PDFs themselves.

## Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/<your-username>/healthbot.git
cd healthbot
pip install -r requirements.txt
```

Add a Gemini API key. For local development, create `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your-gemini-api-key"
```

For Streamlit Cloud deployment, add the same key under the app's Secrets settings instead.

Build the vector index. This only needs to be re-run when the PDFs in `data/` change:

```bash
python ingest.py
```

Then start the app:

```bash
streamlit run app.py
```

## Safety Boundaries

The system prompt avoids giving medical diagnoses and redirects those questions to a qualified professional. It also includes a separate check for messages suggesting a mental health crisis or self-harm, prompting a careful, non-dismissive response. These are guardrails, not a substitute for an actual doctor, registered dietitian, or crisis line.

