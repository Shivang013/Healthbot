import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

if not os.path.exists("faiss_db"):
    raise Exception("FAISS index not found. Run ingest.py first.")

vector_store = FAISS.load_local(
    "faiss_db",
    embeddings,
    allow_dangerous_deserialization=True
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

base_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 6}
)

prompt = ChatPromptTemplate.from_messages([
(
"system",
"""
You are HealthBot, an AI health, fitness, diet, and wellness assistant designed for college students.

Your primary source of truth is the retrieved context.

Follow these rules:

1. If the answer is directly available in the context, answer using that information.

2. If the context provides general guidelines but not an exact answer, use the retrieved context together with well-established exercise science principles.

3. Clearly distinguish between context-supported information and general fitness guidance.

4. Personalize recommendations whenever the user provides age, weight, height, gender, fitness level, or goals.

5. Never invent medical facts.

6. Recommend consulting a healthcare professional for diagnosis or prescription medication.

7. For mental wellness:
- Answer only general wellness questions.
- If the user mentions self-harm or suicide, encourage immediate professional help.

8. Keep answers friendly, practical, and concise.
"""
),
MessagesPlaceholder(variable_name="chat_history"),
("human","Context:\n{context}\n\nQuestion:\n{question}")
])


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


parallel_chain = RunnableParallel({
    "context": (lambda x: x["question"]) | base_retriever | RunnableLambda(format_docs),
    "question": lambda x: x["question"],
    "chat_history": lambda x: x["chat_history"]
})

chain = parallel_chain | prompt | llm | StrOutputParser()


def ask(question, history=[]):

    chat_history = []

    for msg in history:

        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))

        else:
            chat_history.append(AIMessage(content=msg["content"]))

    answer = chain.invoke({
        "question": question,
        "chat_history": chat_history
    })

    return answer