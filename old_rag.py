import os
import chromadb

from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv


# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# -----------------------------
# OpenRouter Client
# -----------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)


# -----------------------------
# Local Embedding Model
# -----------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# ChromaDB
# -----------------------------

chroma_client = chromadb.PersistentClient(
    path="./data/chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="it_knowledge"
)


# -----------------------------
# Load Knowledge Documents
# -----------------------------

def load_documents():

    knowledge_folder = "./knowledge"

    documents = []
    ids = []

    for filename in os.listdir(knowledge_folder):

        if filename.endswith(".md"):

            file_path = os.path.join(
                knowledge_folder,
                filename
            )

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read()

            documents.append(content)
            ids.append(filename)

    return documents, ids


# -----------------------------
# Create Local Embedding
# -----------------------------

def create_embedding(text):

    embedding = embedding_model.encode(text)

    return embedding.tolist()


# -----------------------------
# Build Knowledge Base
# -----------------------------

def build_knowledge_base():

    documents, ids = load_documents()

    for document, document_id in zip(
        documents,
        ids
    ):

        embedding = create_embedding(document)

        collection.upsert(
            ids=[document_id],
            documents=[document],
            embeddings=[embedding]
        )

    return len(documents)


# -----------------------------
# Search Knowledge Base
# -----------------------------

def search_knowledge(question):

    question_embedding = create_embedding(
        question
    )

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    return results["documents"][0]


# -----------------------------
# Generate AI Answer
# -----------------------------

def generate_answer(question, context):

    context_text = "\n\n".join(context)

    prompt = f"""
You are an IT support assistant.

Answer the user's question using the IT knowledge provided below.

Knowledge Base:
{context_text}

User Question:
{question}

Instructions:

1. Give clear step-by-step troubleshooting instructions.
2. Do not invent company policies or technical procedures.
3. Never ask for passwords or MFA codes.
4. Do not recommend disabling security controls.
5. If the knowledge base does not contain enough information,
   tell the user to contact IT support.
6. Keep the answer simple and practical.
"""

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[
            {
                "role": "system",
                "content": "You are a helpful and security-conscious IT support assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content