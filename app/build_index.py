import os
import chromadb
import ollama
from pypdf import PdfReader

DOCUMENTS_DIR = "documents"
DB_DIR = "database"
EMBEDDING_MODEL = "nomic-embed-text"

client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(name="research_documents")


def read_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text += f"\n[Page {page_number}]\n{page_text}\n"

    return text


def split_text(text, chunk_size=200, overlap=40):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks


def get_embedding(text):
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]


def build_index():
    doc_id = 0

    pdf_files = [f for f in os.listdir(DOCUMENTS_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in documents folder.")
        return

    for filename in pdf_files:
        file_path = os.path.join(DOCUMENTS_DIR, filename)
        print(f"Reading: {filename}")

        text = read_pdf(file_path)
        chunks = split_text(text)

        for chunk_number, chunk in enumerate(chunks, start=1):
            embedding = get_embedding(chunk)

            collection.add(
                ids=[str(doc_id)],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[
                    {
                        "source": filename,
                        "chunk_number": chunk_number
                    }
                ]
            )

            doc_id += 1

    print("Final RAG database created successfully.")
    print(f"Total chunks stored: {doc_id}")


build_index()
