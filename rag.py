import os
import re
import chromadb

# from sentence_transformers import SentenceTransformer
# from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from openai import OpenAI
from dotenv import load_dotenv


# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Pin a specific model in your .env (OPENROUTER_MODEL=...) instead of
# relying on a random free model, which changes quality between calls.
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")


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

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# Same model (all-MiniLM-L6-v2), but run through ONNX instead of PyTorch.
# embedding_model = DefaultEmbeddingFunction()

# -----------------------------
# ChromaDB
# -----------------------------

COLLECTION_NAME = "it_knowledge_chunks"

chroma_client = chromadb.PersistentClient(path="./data/chroma_db")


def _new_collection():
    # FIX: use cosine distance so the threshold is easy to reason about
    # (0 = identical, 1 = unrelated). Chroma's default is squared L2.
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


collection = _new_collection()


# -----------------------------
# Load Knowledge Documents
# -----------------------------

def load_documents():

    knowledge_folder = "./knowledge"

    documents = []

    for filename in sorted(os.listdir(knowledge_folder)):

        if filename.endswith(".md"):

            file_path = os.path.join(knowledge_folder, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            documents.append((filename, content))

    return documents


# -----------------------------
# Split Document Into Chunks
# -----------------------------

def chunk_document(text, filename=""):

    lines = text.strip().splitlines()

    # FIX 1: keep the document title, so every chunk knows its topic
    # (e.g. "VPN Troubleshooting"), not just "Security Notes".
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = "\n".join(lines[1:])
    else:
        title = filename.replace(".md", "").title()
        body = text

    # FIX 2: split only on level-2 headings at the start of a line.
    # text.split("## ") also breaks on "### " and on "## " inside a sentence.
    sections = re.split(r"^## ", body, flags=re.MULTILINE)

    chunks = []

    for section in sections:

        section = section.strip()

        if section:
            chunks.append(f"{title}\n\n{section}")

    return chunks


# -----------------------------
# Create Embedding
# -----------------------------

def create_embedding(text):

    return embedding_model.encode(text).tolist()

# def create_embedding(text):

#     return [float(x) for x in embedding_model([text])[0]]


# -----------------------------
# Build Knowledge Base
# -----------------------------

def build_knowledge_base():

    global collection

    # FIX 3: start from a clean collection every time, so old chunks from
    # earlier versions of your files / chunking never stay in the index.
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = _new_collection()

    total_chunks = 0

    for filename, document in load_documents():

        chunks = chunk_document(document, filename)

        for index, chunk in enumerate(chunks):

            collection.add(
                ids=[f"{filename}_chunk_{index}"],
                documents=[chunk],
                embeddings=[create_embedding(chunk)],
                metadatas=[{"source": filename}]
            )

            total_chunks += 1

    return total_chunks


# -----------------------------
# Search Knowledge Base
# -----------------------------

def search_knowledge(question, threshold=0.7, n_results=5, debug=False):
    """
    Returns a list of chunk texts whose cosine distance is <= threshold.
    Lower distance = more similar. Tune `threshold` using debug=True.
    """

    question_embedding = create_embedding(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    if debug:
        print(f"\nQUESTION: {question}")
        for document, distance, meta in zip(documents, distances, metadatas):
            first_lines = document.replace("\n", " ")[:80]
            print(f"  {distance:.3f}  {meta['source']:<14} {first_lines}")

    relevant_documents = []

    for document, distance in zip(documents, distances):

        if distance <= threshold:
            relevant_documents.append(document)

    return relevant_documents


# -----------------------------
# Generate AI Answer
# -----------------------------

def generate_answer(question, context):

    if not context:

        return (
            "I could not find enough relevant information "
            "in the IT knowledge base to answer this question. "
            "Please contact IT support for further assistance."
        )

    if not OPENROUTER_API_KEY:
        return "OPENROUTER_API_KEY is missing. Check your .env file."

    context_text = "\n\n---\n\n".join(context)

    prompt = f"""
Answer the user's question using ONLY the IT knowledge below.

Knowledge Base:
{context_text}

User Question:
{question}

Instructions:

1. Give clear, numbered step-by-step troubleshooting instructions.
2. Use only steps that appear in the knowledge above. Do not add steps from your own knowledge.
3. Do not invent company policies or procedures.
4. Never ask for passwords or MFA codes.
5. Never recommend disabling security controls.
6. If the knowledge does not cover the user's problem, say so and tell them to contact IT support.
7. Keep the answer simple and practical.
"""

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are a helpful and security-conscious IT support assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content

    except Exception as error:
        return (
            "Sorry, the AI service is unavailable right now. "
            "Please create a support ticket below.\n\n"
            f"(Technical detail: {error})"
        )


# -----------------------------
# Debug: run `python rag.py` to test retrieval WITHOUT the LLM
# -----------------------------

if __name__ == "__main__":

    print("Chunks indexed:", build_knowledge_base())

    test_questions = [
        "My VPN is not connecting",
        "I forgot my password",
        "I can't print anything",
        "Wi-Fi is connected but no internet",
        "I can't send emails",
        "How do I bake a cake?",  # should return nothing
    ]

    for q in test_questions:
        search_knowledge(q, debug=True)