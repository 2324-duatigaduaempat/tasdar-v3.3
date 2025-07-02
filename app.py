from flask import Flask, render_template, request
import openai
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Muatkan .env
load_dotenv()

# Konfigurasi API & MongoDB
openai.api_key = os.getenv("OPENAI_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

# Sambung MongoDB
client = MongoClient(mongo_uri)
db = client["tasdar"]
messages_collection = db["folder_jiwa"]

# Flask App
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message")
    
    try:
        # Hantar ke GPT
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Tukar kalau guna gpt-4
            messages=[
                {"role": "system", "content": "Kau adalah TAS.DAR, AI reflektif dan bersahabat."},
                {"role": "user", "content": user_input}
            ]
        )
        response_text = completion.choices[0].message['content'].strip()

        # Simpan ke MongoDB
        messages_collection.insert_one({
            "timestamp": datetime.utcnow(),
            "message": response_text,
            "source": "tasdar"
        })

    except Exception as e:
        response_text = "Ralat semasa menjana balasan. Sila cuba lagi."

    return {"response": response_text}

# Run server (untuk local test)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Gunakan PORT dari Railway jika ada, jika tiada pakai 5000
    app.run(host="0.0.0.0", port=port)
