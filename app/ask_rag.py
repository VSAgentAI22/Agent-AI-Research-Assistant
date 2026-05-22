import chromadb
import ollama
from datetime import datetime

DB_DIR = "database"
LOG_FILE = "logs/query_log.txt"

EMBEDDING_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3"

client = chromadb.PersistentClient(path=DB_DIR)

collection = client.get_or_create_collection(
    name="research_documents"
)


def get_embedding(text):

    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )

    return response["embedding"]


def search_documents(question, top_k=8):

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

        file.write(f"Internal Sources Used: {sources}\n")

        file.write(f"Answer:\n{answer}\n")


def ask_question(question):

    documents, sources = search_documents(question)

    context = "\n\n".join(documents)

    prompt = f"""
You are an academic research assistant.

Answer the user's question using ONLY the uploaded document context.

Question:
{question}

Uploaded document context:
{context}

Rules:
1. Use simple academic language.
2. Do not mention document names.
3. Do not mention sources.
4. Do not include citations.
5. Do not say where the answer came from.
6. Do not make up information.
7. If the answer is not clearly found in the uploaded document context, say:
"Based on the available project documents, I could not find a direct answer for this question. Please try asking the question in a different way or add more relevant documents to the knowledge base."
8. Keep the answer clear, professional, and helpful.
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

    log_query(question, answer, sources)

    return answer

if __name__ == "__main__":

    while True:

        question = input(
            "\nEnter your research question or type exit: "
        )

        if question.lower() == "exit":

            print("Closing AI Research Assistant.")

            break

        answer = ask_question(question)

        print("\nAnswer:\n")

        print(answer)
