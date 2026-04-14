from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

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

if __name__ == "__main__":
    app.run(debug=True)