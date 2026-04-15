import pandas as pd
import joblib
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "dataset", "price_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# encoders
product_encoder = LabelEncoder()
size_encoder = LabelEncoder()

df["product_name"] = product_encoder.fit_transform(df["product_name"])
df["size"] = size_encoder.fit_transform(df["size"])

X = df[["product_name", "size", "quantity", "complexity"]]
y = df["price"]

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X, y)

joblib.dump(model, os.path.join(MODEL_DIR, "price_model.pkl"))
joblib.dump(product_encoder, os.path.join(MODEL_DIR, "product_encoder.pkl"))
joblib.dump(size_encoder, os.path.join(MODEL_DIR, "size_encoder.pkl"))

print("Model trained and saved.")