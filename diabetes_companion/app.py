from flask import Flask, request, jsonify
from chatbot import DiabetesChatbot
from knowledge_base import get_retriever
from supabase_client import SupabaseClient
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

# Debug print to verify environment variable
print("GROQ_API_KEY loaded:", bool(os.getenv("GROQ_API_KEY")))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize retriever from knowledge base
retriever = get_retriever()

# Initialize LLM (ChatGroq)
llm_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=llm_api_key
)

# Initialize chatbot
chatbot = DiabetesChatbot(retriever=retriever, llm=llm)

# Initialize supabase client (stub for now)
supabase_client = SupabaseClient()

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    print("Received request:", request.get_json())  # Debug log
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            print("No message in request")  # Debug log
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        print(f"Processing message: {user_message}")  # Debug log
        response = chatbot.chat(user_message)
        print(f"Sending response: {response}")  # Debug log
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
