import os
from dotenv import load_dotenv  # <--- NEW IMPORT
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

# 1. Load the secrets from the .env file
load_dotenv()

# 2. Get the key safely
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ Error: GOOGLE_API_KEY not found. Did you create the .env file?")
    exit()

# 3. Setup the "Brain" (Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    google_api_key=GOOGLE_API_KEY, 
    temperature=0
)

# 2. Setup the "Memory" (Same as before)
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

# 3. Create the "Thinking Chain"
# This connects the Brain (LLM) to the Memory (Vector DB)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff", # "Stuff" means "stuff all the context into the prompt"
    retriever=db.as_retriever(search_kwargs={"k": 5}), # Retrieve top 5 matches
    return_source_documents=True # Show us WHICH page it found the answer on
)

# 4. The Loop (Ask questions forever!)
print("\n🤖 Policy Navigator is Ready! (Type 'exit' to stop)\n")

while True:
    query = input("❓ Ask a question: ")
    if query.lower() == "exit":
        break
    
    print("   Thinking...")
    
    # Run the query
    result = qa_chain.invoke({"query": query})
    
    # Print the Answer
    print("\n✅ Answer:")
    print(result["result"])
    
    # Optional: Show sources (Pro feature!)
    print("\n📚 Sources Used:")
    for doc in result["source_documents"]:
        print(f" - {doc.page_content[:100]}...") # Print first 100 chars of source
    print("-" * 50)