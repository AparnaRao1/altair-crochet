import os
import re
import random
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------------
# FAQ LOAD
# -----------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE_DIR, "docs", "faq.txt")


def load_faq():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        lines = [x.strip() for x in f.readlines() if x.strip()]
    return lines


faq_chunks = load_faq()

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2)
)

faq_vectors = vectorizer.fit_transform(faq_chunks)


def retrieve_faq(query):
    q = vectorizer.transform([query])
    scores = cosine_similarity(q, faq_vectors)[0]

    best = scores.argmax()

    if scores[best] > 0.08:
        return faq_chunks[best]

    return None


# -----------------------------------
# MEMORY
# -----------------------------------

memory = {
    "flow": None,
    "data": {}
}


# -----------------------------------
# HELPERS
# -----------------------------------

def reset_memory():
    memory["flow"] = None
    memory["data"] = {}


def contains_any(text, words):
    return any(w in text for w in words)




def get_reply(msg, df):
    text = msg.lower().strip()


    if contains_any(text, ["hi", "hello", "hey"]):
        return random.choice([
            "Hello. Welcome to Altair Crochet. How may I help you today?",
            "Hi there. Looking for something custom or cute today?",
            "Hello. I'd love to help you find the perfect crochet piece."
        ])

   

    if memory["flow"] == "cardigan":

        if "size" not in memory["data"]:
            memory["data"]["size"] = msg.upper()
            return "Perfect. What colours would you like?"

        elif "colour" not in memory["data"]:
            memory["data"]["colour"] = msg
            return "Lovely. Would you like regular fit or oversized?"

        elif "fit" not in memory["data"]:
            memory["data"]["fit"] = msg

            size = memory["data"]["size"]
            colour = memory["data"]["colour"]
            fit = memory["data"]["fit"]

            reset_memory()

            return f"Beautiful choice. Custom butterfly cardigan in {colour}, size {size}, {fit} fit. Estimated price starts from ₹2499. Dispatch time is minimum 20 days."

    if memory["flow"] == "plushie":

        if "character" not in memory["data"]:
            memory["data"]["character"] = msg
            return "Cute choice. What colours would you like?"

        elif "colour" not in memory["data"]:
            memory["data"]["colour"] = msg
            return "What size would you prefer? (small / medium / large)"

        elif "size" not in memory["data"]:
            memory["data"]["size"] = msg

            ch = memory["data"]["character"]
            col = memory["data"]["colour"]
            size = memory["data"]["size"]

            reset_memory()

            return f"Lovely. Custom plushie of {ch} in {col}, size {size}. Estimated pricing starts from ₹1299. Dispatch time is minimum 20 days."

    if memory["flow"] == "top":

        if "size" not in memory["data"]:
            memory["data"]["size"] = msg.upper()
            return "Great. What colours would you like?"

        elif "colour" not in memory["data"]:
            memory["data"]["colour"] = msg
            return "Would you like fitted style, loose fit or tie-back style?"

        elif "fit" not in memory["data"]:
            memory["data"]["fit"] = msg

            s = memory["data"]["size"]
            c = memory["data"]["colour"]
            f = memory["data"]["fit"]

            reset_memory()

            return f"Lovely. Custom crochet top in {c}, size {s}, {f}. Estimated pricing starts from ₹2499."

   

    if contains_any(text, ["butterfly cardigan", "custom cardigan","custom top","top","clothes","dress"]):
        reset_memory()
        memory["flow"] = "cardigan"
        return "Absolutely. What size would you like? (XS / S / M / L / XL)"

    if contains_any(text, ["custom plushie", "plushie"]):
        reset_memory()
        memory["flow"] = "plushie"
        return "Absolutely. Which character / animal would you like?"

    if contains_any(text, ["custom boquet", "flowers", "rose","tulip","sunflower"]):
        reset_memory()
        memory["flow"] = "top"
        return "Absolutely. What color would you like?"

   

    nums = re.findall(r"\d+", text)

    if "under" in text and nums:
        budget = int(nums[0])

        matches = df[df["price"] <= budget]["name"].head(5).tolist()

        if matches:
            return "Lovely options in your budget: " + ", ".join(matches)


    for _, row in df.iterrows():
        name = str(row["name"]).lower()

        if name in text:
            return f"{row['name']} is available for ₹{row['price']}. Would you like to place an order or customise colours?"

    

    rag = retrieve_faq(text)

    if rag:
        return rag

    

    return "Contact @altair.crochet on instagram or +91 6364244719 on whatsapp."