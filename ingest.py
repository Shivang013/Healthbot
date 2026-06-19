import os
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

print("Loading PDFs...")

loader = DirectoryLoader(
    "data",
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=True
)

docs = loader.load()

print(f"Loaded {len(docs)} pages")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(docs)

print(f"Created {len(chunks)} chunks")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Creating FAISS index...")

vector_store = FAISS.from_documents(
    chunks,
    embeddings
)

vector_store.save_local("faiss_db")

print("✅ FAISS index saved successfully!")