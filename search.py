from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# 1. Setup the Embedding Model (Must be same as before!)
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Connect to our existing Database
# We tell it "look in the chroma_db folder"
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# 3. Ask a Question
query = "What are the rights of a consumer?"
print(f"\n🔎 Searching for: '{query}'\n")

# 4. Search the DB for the top 3 matches
results = db.similarity_search(query, k=3)

# 5. Print the results
print("--- Found these relevant sections ---")
for i, doc in enumerate(results):
    print(f"\n📄 Match {i+1}:")
    print(doc.page_content[:300] + "...") # Show first 300 characters
    print("-" * 50)