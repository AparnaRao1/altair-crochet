# backend/chatbot.py
# GPT-LIKE PREMIUM CHATBOT
# Smart intent understanding
# Image generation
# Price prediction
# FAQ RAG
# Natural ecommerce assistant

import os
import re
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from image_generator import generate_image
from price_predictor import predict_price


# ---------------------------------------------------
# FAQ LOAD
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE_DIR, "docs", "faq.txt")


def load_faq():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


faq_chunks = load_faq()

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2)
)

faq_vectors = vectorizer.fit_transform(faq_chunks)


def faq_search(query):
    q = vectorizer.transform([query])
    scores = cosine_similarity(q, faq_vectors)[0]

    best = scores.argmax()

    if scores[best] > 0.10:
        return faq_chunks[best]

    return None


# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def get_cm(text):
    nums = re.findall(r"\d+", text)
    if nums:
        return int(nums[0])
    return 25


def get_qty(text):
    qty_match = re.search(r"qty\s*(\d+)", text)
    if qty_match:
        return int(qty_match.group(1))
    return 1


def size_from_cm(cm):
    if cm <= 15:
        return "S"
    elif cm <= 25:
        return "M"
    else:
        return "L"


def has_any(text, words):
    return any(word in text for word in words)


# ---------------------------------------------------
# MAIN CHATBOT
# ---------------------------------------------------

def get_reply(msg, df):
    text = msg.lower().strip()

    # ---------------------------------------------------
    # CUSTOM ORDER HELP
    # ---------------------------------------------------

    if "custom order" in text:
        return {
            "reply": """Absolutely ✨ Please describe your custom order like this:

Product:
Theme:
Colour:
Size:
Quantity:

Example:
Tanjiro plushie green black 25 cm qty 2"""
        }

    # ---------------------------------------------------
    # SMART PLUSHIE INTENT
    # ---------------------------------------------------

    if has_any(text, [
        "plushie",
        "amigurumi",
        "doll",
        "preview plushie",
        "anime plushie",
        "toy"
    ]):

        cm = get_cm(text)
        qty = get_qty(text)
        size = size_from_cm(cm)

        theme = "custom character"

        anime_names = [
            "tanjiro",
            "naruto",
            "gojo",
            "luffy",
            "zoro",
            "nezuko",
            "itachi",
            "goku"
        ]

        for name in anime_names:
            if name in text:
                theme = name.title()

        prompt = f"""
        handmade crochet amigurumi plushie,
        {theme},
        anime inspired yarn doll,
        premium product photography,
        soft yarn texture,
        white background
        """

        filename = generate_image(prompt)

        price = predict_price(
            "Custom Plushie",
            size,
            qty,
            3
        )

        return {
            "reply": f"""Here is a preview of your custom {theme} plushie.

Approx Size: {cm} cm
Quantity: {qty}

Estimated Price: ₹{price}
Dispatch Time: Minimum 20 days from order confirmation.

Would you like to proceed?""",
            "image": f"/generated/{filename}" if filename else None
        }

    # ---------------------------------------------------
    # CARDIGAN INTENT
    # ---------------------------------------------------

    if has_any(text, [
        "cardigan",
        "butterfly cardigan",
        "crochet jacket",
        "sweater"
    ]):

        size = "M"

        if "xl" in text:
            size = "XL"
        elif "l" in text:
            size = "L"
        elif "s" in text:
            size = "S"

        prompt = """
        luxury butterfly crochet cardigan,
        elegant fashion photography,
        premium handmade yarn clothing,
        clean white background
        """

        filename = generate_image(prompt)

        price = predict_price(
            "Butterfly Cardigan",
            size,
            1,
            4
        )

        return {
            "reply": f"""Here is a preview of your custom cardigan.

Size: {size}
Estimated Price: ₹{price}

Dispatch Time: Minimum 20 days from order confirmation.""",
            "image": f"/generated/{filename}" if filename else None
        }

    # ---------------------------------------------------
    # CROCHET TOP INTENT
    # ---------------------------------------------------

    if has_any(text, [
        "crochet top",
        "top",
        "butterfly top",
        "halter top"
    ]):

        size = "M"

        if "xl" in text:
            size = "XL"
        elif "l" in text:
            size = "L"
        elif "s" in text:
            size = "S"

        prompt = """
        stylish handmade crochet top,
        aesthetic fashion product photo,
        premium yarn clothing,
        white background
        """

        filename = generate_image(prompt)

        price = predict_price(
            "Crochet Top",
            size,
            1,
            3
        )

        return {
            "reply": f"""Here is a preview of your crochet top.

Size: {size}
Estimated Price: ₹{price}

Dispatch Time: Minimum 20 days from order confirmation.""",
            "image": f"/generated/{filename}" if filename else None
        }

    # ---------------------------------------------------
    # BOUQUET / FLOWER INTENT
    # ---------------------------------------------------

    if has_any(text, [
        "bouquet",
        "flowers",
        "tulip",
        "rose",
        "sunflower",
        "gift bouquet"
    ]):

        prompt = """
        handmade crochet flower bouquet,
        tulips roses sunflowers,
        elegant wrapping,
        premium gift photography,
        white background
        """

        filename = generate_image(prompt)

        return {
            "reply": """Here is a preview of a crochet bouquet.

Estimated Price: ₹1299 onwards

Dispatch Time: Minimum 20 days from order confirmation.""",
            "image": f"/generated/{filename}" if filename else None
        }

    # ---------------------------------------------------
    # BUDGET SEARCH
    # ---------------------------------------------------

    if "under" in text:

        nums = re.findall(r"\d+", text)

        if nums:
            budget = int(nums[0])

            matches = df[df["price"] <= budget]["name"].head(5).tolist()

            if matches:
                return {
                    "reply": "Lovely options in your budget: " + ", ".join(matches)
                }

    # ---------------------------------------------------
    # PRODUCT LOOKUP
    # ---------------------------------------------------

    for _, row in df.iterrows():

        if str(row["name"]).lower() in text:
            return {
                "reply": f"{row['name']} is available for ₹{row['price']}. Would you like to place an order?"
            }

    # ---------------------------------------------------
    # FAQ RAG
    # ---------------------------------------------------

    rag = faq_search(text)

    if rag:
        return {
            "reply": rag
        }

    # ---------------------------------------------------
    # GREETINGS
    # ---------------------------------------------------

    if re.search(r"\b(hi|hello|hey|hii|heyy)\b", text):
        return {
            "reply": random.choice([
                "Hello. Welcome to Altair Crochet. How may I help you today?",
                "Hi there. Looking for something cute or custom today?",
                "Hello. I’d love to help you create something beautiful."
            ])
        }

    # ---------------------------------------------------
    # FALLBACK
    # ---------------------------------------------------

    return {
        "reply": """I can help with:

• Custom plushies
• Cardigans
• Crochet tops
• Bouquets
• Pricing
• Dispatch
• Gifts

Try:
'I need Tanjiro plushie 25 cm'
'I need cardigan XL'
'Gift under 1000'"""
    }