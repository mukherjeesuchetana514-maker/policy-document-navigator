import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# 1. Setup
DATA_FOLDER = "./data"
DB_FOLDER = "./chroma_db"

def ingest_all_files():
    print(f"📂 Scanning folder: {DATA_FOLDER} ...")
    
    all_documents = []
    
    # 2. Loop through every file in the folder
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".pdf"):
            file_path = os.path.join(DATA_FOLDER, filename)
            print(f"   📖 Reading: {filename}...")
            
            try:
                # Load the PDF
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                all_documents.extend(documents) # Add to the big pile
                print(f"      ✅ Added {len(documents)} pages.")
            except Exception as e:
                print(f"      ❌ Error reading {filename}: {e}")

    if not all_documents:
        print("⚠️ No PDFs found! Did you put them in the 'data' folder?")
        return

    print(f"\n🧠 Splitting & Embedding {len(all_documents)} total pages...")
    
    # 3. Create the Brain (Vector Database)
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # This builds the database from ALL the files combined
    db = Chroma.from_documents(
        documents=all_documents, 
        embedding=embedding_function, 
        persist_directory=DB_FOLDER
    )
    
    print("🎉 Success! The AI has learned ALL your documents.")

if __name__ == "__main__":
    ingest_all_files()