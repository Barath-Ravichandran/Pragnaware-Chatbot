from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import os

# Load env
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
# 🌍 GLOBAL OBJECTS (INIT EMPTY)
# ========================
db = None
llm = None

# ========================
# 🚀 STARTUP EVENT (IMPORTANT FIX)
# ========================
@app.on_event("startup")
def startup_event():
    global db, llm

    try:
        print("🚀 Starting up...")

        # 📚 Load documents
        loader = TextLoader("company_data.txt", encoding="utf-8")
        documents = loader.load()

        # 🧠 Embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # 📦 Vector DB
        db = FAISS.from_documents(documents, embeddings)

        # 🤖 LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=OPENAI_API_KEY
        )

        print("✅ Startup completed successfully!")

    except Exception as e:
        print("❌ Startup failed:", str(e))


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
# 💬 CHAT (RAG)
# ========================
@app.post("/chat")
def chat(req: ChatRequest):
    global db, llm

    if db is None or llm is None:
        return {"reply": "⚠️ Server is still starting. Please try again in a few seconds."}

    try:
        # 🔍 Retrieve relevant docs
        docs = db.similarity_search(req.message, k=3)
        context = " ".join([doc.page_content for doc in docs])

        # 🤖 Ask LLM
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

# ========================
# 🏠 ROOT CHECK (IMPORTANT)
# ========================
@app.get("/")
def home():
    return {"status": "API is running 🚀"}

# ========================
# ▶️ RUN (LOCAL / RENDER)
# ========================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
