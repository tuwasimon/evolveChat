from flask import Flask, render_template, request, jsonify
import requests
import json
import pandas as pd
import os

app = Flask(__name__)

# Load AI Automation Agency data from JSON
def load_agency_data():
    with open("school_data.json", "r", encoding="utf-8") as file:
        return json.load(file)

agency_data = load_agency_data()

# Save chat history
def save_chat(user, bot_response):
    file_path = "chats.xlsx"
    
    # Check if file exists, otherwise create a new one
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
    else:
        df = pd.DataFrame(columns=["User", "Bot"])

    # Append new chat
    new_chat = pd.DataFrame({"User": [user], "Bot": [bot_response]})
    df = pd.concat([df, new_chat], ignore_index=True)

    # Save to Excel
    df.to_excel(file_path, index=False)

# API Configuration (Update with your API key if needed)
GROQ_API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

user_data = {}

@app.route("/admin")
def admin():
    file_path = "chats.xlsx"

    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        chat_logs = df.to_dict(orient="records")  # Convert to a list of dictionaries
    else:
        chat_logs = []

    return render_template("admin.html", chats=chat_logs)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/store_user', methods=['POST'])
def store_user():
    global user_data
    user_data = request.json  # Save user info
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data["message"]

    bot_response = generate_response(user_input)

    return jsonify({"response": bot_response})

# Fetch data from file
def fetch_data_from_file(user_input):
    """Retrieve service details, pricing, integration options, and contact information."""
    
    user_input_lower = user_input.lower()

    if "services" in user_input_lower or "offer" in user_input_lower:
        service_list = ", ".join(service["name"] for service in agency_data["services"])
        return f"We offer the following AI automation services: {service_list}. Which one do you need details about?"

    for service in agency_data["services"]:
        if service["name"].lower() in user_input_lower:
            return (f"{service['name']}: {service['description']} "
                    f"\n💰 Pricing: {service['price']} "
                    f"\n🔗 Integrations: {', '.join(service['integration'])}.")

    if "contact" in user_input_lower or "reach" in user_input_lower:
        contact = agency_data["location"]
        return f"📞 {contact['contact']} | ✉️ {contact['email']} | 🌐 {contact['website']}."

    if "location" in user_input_lower or "where" in user_input_lower:
        loc = agency_data["location"]
        return f"Our office is located at {loc['address']}, {loc['name']}."

    return None

# Generate chatbot response
def generate_response(user_input):
    """Generate response from API or local file data."""
    
    file_response = fetch_data_from_file(user_input)
    if file_response:
        return file_response  

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are an AI chatbot for Evolve AI Automation Agency. Answer ONLY questions about AI automation services, pricing, integration, and contact details."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": 250
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

if __name__ == '__main__':
    app.run()
