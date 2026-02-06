from flask import Flask, render_template, request, jsonify
import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

app = Flask(__name__)

# ===========================
# 1. SETUP AI (The Brain)
# ===========================
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", # Fixed: standard model name to avoid 404 errors
    google_api_key=api_key, 
    temperature=0
)

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# ===========================
# 2. ROUTES
# ===========================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.json
        query = data.get('query')
        mode = data.get('mode', 'standard') 
        
        # --- SAFETY & KNOWLEDGE INJECTION ---
        # Updated to include specific BNS sections for harassment/rape
        safety_instruction = (
            "IMPORTANT KNOWLEDGE: "
            "1. For 'harassment', refer to Bharatiya Nyaya Sanhita (BNS) Sections 74-79 (Sexual Harassment, Stalking, etc.). "
            "2. For 'rape', refer to BNS Sections 63-70. "
            "CRITICAL INSTRUCTION: If the user mentions 'fraud', 'scam', 'harassment', 'violence', "
            "or 'abuse', you MUST end your answer with this exact text: "
            "'\n\n🚨 **Immediate Action:** Please dial 1930 for Cyber Crime or 112 for Emergency Services.'"
        )

        # --- FEATURE 1: PLAIN LANGUAGE & IMPACT MODES ---
        if mode == 'plain_language':
            enhanced_query = (
                f"You are a Plain Language Translator. Explain this legal concept in simple, plain English "
                f"for a 5th grader. Keep it short. {safety_instruction} \nQuery: {query}"
            )
        elif mode == 'impact':
            enhanced_query = (
                f"You are a Policy Impact Analyst. Analyze the social and economic impact of this policy. "
                f"Who benefits and who loses? {safety_instruction} \nQuery: {query}"
            )
        else:
            # Standard Mode
            enhanced_query = (
                f"You are a Government Policy Expert. Answer strictly based on the provided legal context. "
                f"{safety_instruction} \nQuery: {query}"
            )
            
        print(f"🧠 Processing Mode: {mode} | Query: {enhanced_query}")

        # Run AI
        result = qa_chain.invoke({"query": enhanced_query})
        return jsonify({"answer": result["result"]})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"answer": "Error processing request."}), 500

# --- FEATURE 2: CIVIC ENGAGEMENT (VOTING) ---
@app.route('/vote', methods=['POST'])
def vote():
    try:
        data = request.json
        vote_type = data.get('vote') # 'up' or 'down'
        query = data.get('query')
        
        # Save to a CSV file (Simple "Database" for Hackathons)
        file_exists = os.path.isfile('votes.csv')
        with open('votes.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Date', 'Query', 'Vote']) # Header
            writer.writerow([datetime.now(), query, vote_type])
            
        print(f"🗳️ Vote Recorded: {vote_type}")
        return jsonify({"status": "success", "message": "Vote recorded!"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)