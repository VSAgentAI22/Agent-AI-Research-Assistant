import chromadb
import ollama
from datetime import datetime

DB_DIR = "database"
LOG_FILE = "logs/query_log.txt"

EMBEDDING_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3"

client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(name="research_documents")


def get_embedding(text):
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]


def search_documents(question, top_k=4):
    question_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    sources = results["metadatas"][0]

    return documents, sources


def log_query(question, answer, sources):
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write("\n----------------------------------------\n")
        file.write(f"Date/Time: {datetime.now()}\n")
        file.write(f"Question: {question}\n")
        file.write(f"Sources Used: {sources}\n")
        file.write(f"Answer:\n{answer}\n")


def ask_question(question):
    documents, sources = search_documents(question)

    context = "\n\n".join(documents)
    source_names = list(set([source["source"] for source in sources]))

    prompt = f"""
You are an academic research assistant for Whitireia and WelTec.

Your job is to answer student and staff research questions using ONLY the uploaded research document context.

Question:
{question}

Uploaded document context:
{context}

Rules:
1. Use only the context provided.
2. Do not make up information.
3. If the answer is not found, say:
"I could not find enough information in the uploaded research documents."
4. Use simple academic language.
5. Give a clear and useful answer.
6. At the end, include the source document name.

Source documents:
{source_names}
"""

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    log_query(question, answer, source_names)

    return answer


while True:
    question = input("\nEnter your research question or type exit: ")

    if question.lower() == "exit":
        print("Closing AI Research Assistant.")
        break

    answer = ask_question(question)

    print("\nAnswer:\n")
    print(answer)
