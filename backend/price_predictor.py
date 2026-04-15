# backend/price_predictor.py
# FINAL PRICE PREDICTOR

import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

model = joblib.load(os.path.join(MODEL_DIR, "price_model.pkl"))
product_encoder = joblib.load(os.path.join(MODEL_DIR, "product_encoder.pkl"))
size_encoder = joblib.load(os.path.join(MODEL_DIR, "size_encoder.pkl"))


def predict_price(product_name, size, quantity, complexity):
    try:
        p = product_encoder.transform([product_name])[0]
        s = size_encoder.transform([size])[0]

        X = pd.DataFrame([{
            "product_name": p,
            "size": s,
            "quantity": quantity,
            "complexity": complexity
        }])

        price = model.predict(X)[0]

        return int(round(price))

    except:
        return 1499