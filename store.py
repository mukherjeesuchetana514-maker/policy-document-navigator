import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# 1. Load the text we just extracted
# We use the text file because it's already clean
loader = TextLoader("test_output.txt", encoding="utf-8")
documents = loader.load()

# 2. Split it into chunks
# chunk_size=1000 means "roughly 3-4 paragraphs per chunk"
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

print(f"🧩 Split the document into {len(chunks)} chunks.")

# 3. Setup the Embedding Model (The "Translator")
# This turns text into numbers (vectors) so the AI can understand meaning.
# We use 'all-MiniLM-L6-v2' because it's free, fast, and runs on your laptop!
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Save to ChromaDB (The Database)
print("💾 Saving to database... (This might take a minute)")
db = Chroma.from_documents(
    documents=chunks, 
    embedding=embedding_function, 
    persist_directory="./chroma_db"
)

print(f"✅ Success! Saved {len(chunks)} chunks to the 'chroma_db' folder.")