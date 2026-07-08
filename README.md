# HealthBot

A retrieval-augmented chatbot that answers diet, fitness, and general health questions. Responses are grounded in public health guidelines from WHO, ICMR, and ACSM, with Google Gemini handling generation.

## Overview

General-purpose chatbots will readily answer fitness and nutrition questions, but they rarely cite anything and can drift into confidently incorrect territory. This project retrieves relevant passages from a curated set of public health documents before generating a response, so answers stay traceable to a real source. For questions outside the scope of those documents, it falls back on the model's general reasoning rather than refusing to answer.

## How It Works

The project is split into two independent applications — a FastAPI backend and a React frontend — that communicate over HTTP.

**Ingestion** (`ingest.py`) loads the source PDFs, splits them into overlapping chunks using LangChain's `RecursiveCharacterTextSplitter`, embeds each chunk locally using `sentence-transformers/all-MiniLM-L6-v2`, and writes the result to a FAISS index in `faiss_db/`. This runs once, and again any time the source documents change.

**Serving** (`backend/main.py`) is the FastAPI application. On startup it loads the prebuilt FAISS index and embedding model rather than rebuilding them per request. Each incoming question is embedded, compared against the index to retrieve the top-k most relevant chunks, and passed along with that context into a prompt sent to Gemini. The generated answer is returned as JSON via the `POST /chat` endpoint.

**Frontend** (`frontend/`) is a React (Vite) chat UI. `services/api.js` sends the user's question to the backend via Axios and renders the returned answer as a new message bubble.

Conversation history is currently accepted by the API but not yet used to inform retrieval or generation — each question is answered independently of prior turns.

## Project Structure

```
Health_chatbot/
├── backend/
│   ├── data/            # Source PDFs (gitignored)
│   ├── faiss_db/        # Generated vector index (gitignored)
│   ├── ingest.py         # Builds the FAISS index from source PDFs
│   ├── main.py            # FastAPI app — CORS, endpoints, request validation
│   ├── rag.py               # Embedding, retrieval, and Gemini generation
│   ├── requirements.txt
│   └── .env                 # API keys (gitignored, never committed)
│
├── frontend/
│   ├── src/
│   │   ├── components/     # sidebar, chat, message, input
│   │   ├── services/api.js  # Axios calls to the backend
│   │   └── App.jsx
│   ├── public/
│   └── package.json
│
├── .env.example
├── .gitignore
└── README.md
```

## Tech Stack

- **Frontend** — React (Vite), Axios
- **Backend** — FastAPI, Pydantic
- **Embeddings** — HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- **Vector store** — FAISS
- **Chunking** — LangChain `RecursiveCharacterTextSplitter`
- **LLM** — Google Gemini

## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt --break-system-packages
# add your Gemini API key to backend/.env — see .env.example
uvicorn main:app --reload
```
Wait for `Application startup complete` before sending requests — the embedding model takes a few seconds to load on startup.

**Frontend** (separate terminal)
```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

If the source PDFs in `backend/data/` change, rebuild the index:
```bash
cd backend
python ingest.py
```

## Environment Variables

Copy `.env.example` to `backend/.env` and add your own key:
```
GEMINI_API_KEY=your_key_here
```
`.env` is gitignored and must never be committed.

## Current Limitations

- No multi-turn memory — each question is answered independently of chat history.
- CORS is currently restricted to `http://localhost:5173` for local development; update `allow_origins` in `main.py` before deploying elsewhere.
