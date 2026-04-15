from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import os

from chatbot import get_reply

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(BASE_DIR, "..", "dataset", "dataset.csv")
GENERATED_DIR = os.path.join(BASE_DIR, "generated")

os.makedirs(GENERATED_DIR, exist_ok=True)




@app.route("/products")
def products():

    df = pd.read_csv(CSV_PATH)

    items = []

    for _, row in df.iterrows():

        filename = os.path.basename(str(row["image"]))

        items.append({
            "id": int(row["id"]),
            "name": row["name"],
            "price": int(row["price"]),
            "category": row["category"],
            "description": row["description"],
            "image": f"/images/{filename}"
        })

    return jsonify(items)




@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    msg = data.get("message", "").strip()

    if not msg:
        return jsonify({
            "reply": "Please type a message."
        })

    df = pd.read_csv(CSV_PATH)

    result = get_reply(msg, df)

    # If chatbot.py returns plain string
    if isinstance(result, str):
        return jsonify({
            "reply": result
        })

   
    return jsonify(result)




@app.route("/generated/<path:filename>")
def generated(filename):
    return send_from_directory(GENERATED_DIR, filename)


# -----------------------------------

if __name__ == "__main__":
    app.run(debug=True)