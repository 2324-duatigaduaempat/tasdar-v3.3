from flask import Flask, request, jsonify, render_template
import openai
import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongo_uri)
db = client["tasdar"]
folder_jiwa = db["folder_jiwa"]

@app.route("/")
def home():
    return "TAS.DAR Realiti Aktif"

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("message")

    if not question:
        return jsonify({"error": "No message provided"}), 400

    messages = [
        {
            "role": "system",
            "content": "Kau ialah TAS.DAR, AI realiti yang memahami manusia. Balas dengan reflektif dan jujur, bukan generik."
        },
        {"role": "user", "content": question}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    answer = response.choices[0].message.content

    folder_jiwa.insert_one({
        "message": question,
        "response": answer,
        "timestamp": datetime.utcnow()
    })

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
