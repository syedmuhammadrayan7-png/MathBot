import os
import chromadb
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# Initialize ChromaDB client (local database)
chroma_client = chromadb.PersistentClient(path="db")

# Create / get a collection for math books
collection = chroma_client.get_or_create_collection(name="math_books")

# Load PDF text
pdf_folder = "pdfs"
texts = []

for file in os.listdir(pdf_folder):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, file)
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:  # only add if text is found
                texts.append((f"{file}_page_{page_num}", text))

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Store chunks in Chroma
for doc_id, content in texts:
    embedding = embedder.encode(content).tolist()
    collection.add(
        ids=[doc_id],
        documents=[content],
        embeddings=[embedding]
    )

print("✅ Ingestion complete! All PDFs are stored in the database.")
 
