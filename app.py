import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Ensure API key is available
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please create a .env file with GEMINI_API_KEY=YOUR_API_KEY")

# Configure the Gemini API
genai.configure(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)

# Store chat history for each user
chat_histories = {}  # Dictionary to store history per user

def ask_gemini(user_id, prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Get user chat history (default to empty list)
        history = chat_histories.get(user_id, [])
        
        # Add user message to history
        history.append({"role": "user", "content": prompt})
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Store bot response in history
        history.append({"role": "bot", "content": response.text})
        
        # Save updated history (limit to last 10 messages)
        chat_histories[user_id] = history[-10:]
        
        return response.text
    except Exception as e:
        return str(e)

# Serve the chatbot HTML page
@app.route("/")
def home():
    return render_template("index.html")  # Serve frontend

# API endpoint for chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request. Please provide a JSON with a 'message' field."}), 400

    user_message = data["message"]
    user_id = data.get("user_id", "default")  # Optional user tracking

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        bot_response = ask_gemini(user_id, user_message)
        
        return jsonify({
            "response": bot_response,
            "history": chat_histories[user_id]  # Send chat history
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
