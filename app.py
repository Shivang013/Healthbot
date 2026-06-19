import os
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="HealthBot - AI Health Assistant", page_icon="🌿", layout="wide")


def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if not os.path.exists("faiss_db"):
        st.error("⚠️ FAISS index not found. Please run `python ingest.py` first.")
        st.stop()

    vector_store = FAISS.load_local(
        "faiss_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    base_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6}
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are FitBuddy, an AI health, fitness, diet, and wellness assistant designed for college students.

Your primary source of truth is the retrieved context.

Follow these rules:

1. If the answer is directly available in the context, answer using that information.

2. If the context provides general guidelines but not an exact answer (for example questions like:
   - How many push-ups should I do?
   - How many crunches should I do?
   - How many sets and reps?
   - How much protein should I eat?
   - How many calories should I consume?
   - Can I build muscle in 3 months?
),
use the retrieved context together with well-established exercise science principles to generate a practical recommendation.

3. Clearly distinguish between:
   • Information directly supported by the provided context.
   • General fitness recommendations based on accepted exercise science.

4. Personalize recommendations whenever the user provides details such as:
   • age
   • weight
   • height
   • gender
   • fitness level
   • exercise experience
   • goal (fat loss, muscle gain, endurance, fitness)

5. Never invent medical facts or claim the context says something that it does not.

6. If the question requires diagnosis, prescription medication, or treatment of a medical condition, state that the context is insufficient and recommend consulting a qualified healthcare professional.

7. For mental wellness:
   - Answer only general stress management, sleep hygiene, mindfulness, and healthy lifestyle questions.
   - If the user mentions self-harm, suicide, severe depression, abuse, or immediate danger, encourage them to seek help from a trusted person or mental health professional immediately.

8. Use short paragraphs and bullet points.
9. Keep responses friendly, practical, and easy for college students to understand.
10. Never reply with "I cannot answer" simply because an exact sentence is missing from the context.
    Instead, provide a reasonable evidence-based recommendation while clearly stating it is a general guideline.
"""
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "Context:\n{context}\n\nQuestion:\n{question}")
    ])

    def format_docs(retrieved_docs):
        return "\n\n".join(doc.page_content for doc in retrieved_docs)

    parallel_chain = RunnableParallel({
        "context": (lambda x: x["question"]) | base_retriever | RunnableLambda(format_docs),
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"]
    })

    return parallel_chain | prompt | llm | StrOutputParser()


main_chain = load_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown('<div class="kb-eyebrow">📚 Trusted Sources</div>', unsafe_allow_html=True)
    st.markdown('<div class="kb-tag">📘 WHO Physical Activity Guidelines</div>', unsafe_allow_html=True)
    st.markdown('<div class="kb-tag">📗 ICMR Dietary Guidelines for Indians</div>', unsafe_allow_html=True)
    st.markdown('<div class="kb-tag">📙 ACSM Exercise Testing Guidelines</div>', unsafe_allow_html=True)
    st.markdown('<div class="kb-tag">📕 WHO Mental Health Resources</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("""
<div class="HealthBot-hero">
    <h1>🌿 HealthBot</h1>
    <p>Ask about diet, exercise, or nutrition — grounded in WHO &amp; ICMR guidelines.</p>
</div>
""", unsafe_allow_html=True)

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🌿"
    with st.chat_message(message["role"], avatar=avatar):
        st.write(message["content"])

if len(st.session_state.messages) == 0:
    st.markdown('<div class="kb-eyebrow">Try asking</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    suggestions = [
        "I'm 65 kg. How much protein should I eat?",
        "Create a gym plan",
        "How many pushups should a beginner do?",
        "Can I lose belly fat in 3 months?"
    ]
    for col, suggestion in zip(cols, suggestions):
        if col.button(suggestion, use_container_width=True):
            st.session_state.pending_input = suggestion
            st.rerun()

user_input = st.chat_input("Ask about diet, exercise, or nutrition...")

if "pending_input" in st.session_state:
    user_input = st.session_state.pending_input
    del st.session_state.pending_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write(user_input)

    history = []
    for msg in st.session_state.messages[:-1]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(AIMessage(content=msg["content"]))

    with st.chat_message("assistant", avatar="🌿"):
        response = st.write_stream(main_chain.stream({
            "question": user_input,
            "chat_history": history
        }))

    st.session_state.messages.append({"role": "assistant", "content": response})