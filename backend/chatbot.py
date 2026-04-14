import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE_DIR, "docs", "faq.txt")

def load_chunks():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = [line.strip() for line in text.split("\n") if line.strip()]
    return chunks

faq_chunks = load_chunks()

vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
faq_vectors = vectorizer.fit_transform(faq_chunks)

def retrieve_context(query, top_k=3):
    q = vectorizer.transform([query])
    scores = cosine_similarity(q, faq_vectors)[0]

    ranked = scores.argsort()[::-1][:top_k]
    results = []

    for idx in ranked:
        if scores[idx] > 0.08:
            results.append(faq_chunks[idx])

    return results

def generate_answer(query, contexts):
    if not contexts:
        return "I can help with crochet orders, dispatch, pricing, gifting and custom requests."

    # join top relevant lines naturally
    answer = " ".join(contexts[:2])

    return answer

def get_reply(msg, df):
    query = msg.lower().strip()

    # product lookup only if direct match
    for _, row in df.iterrows():
        if str(row["name"]).lower() in query:
            return f"{row['name']} is available for ₹{row['price']}. {row['description']}"

    contexts = retrieve_context(query)

    return generate_answer(query, contexts)