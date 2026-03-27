from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import os

# Load env (optional)
from dotenv import load_dotenv
load_dotenv()

# ========================
# 📚 LANGCHAIN IMPORTS
# ========================
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_openai import ChatOpenAI

# ========================
# 🚀 APP INIT
# ========================
app = FastAPI()

# ========================
# 🔑 OPENAI KEY
# ========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ========================
# 📚 LOAD DATA (UTF-8 FIX)
# ========================
loader = TextLoader("company_data.txt", encoding="utf-8")
documents = loader.load()

# ========================
# 🧠 EMBEDDINGS (FREE)
# ========================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ========================
# 📦 VECTOR DB
# ========================
db = FAISS.from_documents(documents, embeddings)

# ========================
# 🤖 LLM (OPENAI)
# ========================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    openai_api_key=OPENAI_API_KEY
)

# ========================
# 💾 DATABASE
# ========================
conn = sqlite3.connect("leads.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT
)
""")

# ========================
# 📦 REQUEST MODELS
# ========================
class Lead(BaseModel):
    name: str
    email: str

class ChatRequest(BaseModel):
    message: str

# ========================
# 💾 SAVE LEAD
# ========================
@app.post("/save-lead")
def save_lead(lead: Lead):
    cursor.execute(
        "INSERT INTO leads (name, email) VALUES (?, ?)",
        (lead.name, lead.email)
    )
    conn.commit()
    return {"status": "saved"}

# ========================
# 💬 CHAT (RAG WORKING)
# ========================
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        # 🔍 Step 1: Retrieve relevant data
        docs = db.similarity_search(req.message, k=3)
        context = " ".join([doc.page_content for doc in docs])

        # 🤖 Step 2: Ask LLM
        response = llm.invoke([
            {
                "role": "system",
                "content": "You are Pragnaware Solutions assistant. Answer only from the provided company data. Be professional and clear."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {req.message}"
            }
        ])

        return {"reply": response.content}

    except Exception as e:
        return {"reply": str(e)}

# ========================
# 📊 VIEW LEADS
# ========================
@app.get("/leads")
def get_leads():
    cursor.execute("SELECT * FROM leads")
    return cursor.fetchall()