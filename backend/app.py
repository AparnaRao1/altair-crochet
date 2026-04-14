from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
from flask import request
from chatbot import get_reply

app = Flask(__name__)
CORS(app)

CSV_PATH = "../dataset/dataset.csv"

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
    data = request.json
    msg = data["message"]

    df = pd.read_csv("../dataset/dataset.csv")

    reply = get_reply(msg, df)

    return {"reply": reply}
if __name__ == "__main__":
    app.run(debug=True)