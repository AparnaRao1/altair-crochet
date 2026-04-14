import pandas as pd

FAQS = {
    "dispatch": "Dispatch time is minimum 20 days from order date.",
    "delivery": "Dispatch begins after crafting. Delivery depends on location.",
    "color": "Yes, custom colors are available for most products.",
    "bulk": "Yes, bulk and gifting orders are accepted.",
    "handmade": "All Altair Crochet products are handmade."
}

def get_reply(msg, df):
    text = msg.lower()

    if "dispatch" in text or "how long" in text:
        return FAQS["dispatch"]

    if "color" in text or "custom colour" in text or "custom color" in text:
        return FAQS["color"]

    if "bulk" in text:
        return FAQS["bulk"]

    if "gift" in text and "1000" in text:
        return "Recommended: Tulip Bouquet, Bow Keychain."

    if "under" in text:
        prices = [int(s) for s in text.split() if s.isdigit()]
        if prices:
            budget = prices[0]
            items = df[df["price"] <= budget]["name"].head(3).tolist()
            if items:
                return "Recommended: " + ", ".join(items)

    return "Please describe what you'd like. I can help with products, custom orders, colors, dispatch, and recommendations."