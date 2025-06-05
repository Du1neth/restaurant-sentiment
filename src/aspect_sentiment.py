# src/aspect_sentiment.py

import re
from transformers import pipeline

# 1) Initialize the Hugging Face sentiment pipeline once at import time
#    (You may need to set TRANSFORMERS_NO_TF=1 in your environment before running.)
SENTIMENT_PIPELINE = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# 2) Use our expanded keyword lists for each aspect:
ASPECT_KEYWORDS = {
    "service": [
        "service", "waiter", "server", "staff", "attentive", "rude",
        "slow", "friendly", "host", "hostess", "bartender", "manager",
        "unhelpful", "polite", "wait", "rush", "greet"
    ],
    "food": [
        "food", "dish", "meal", "taste", "flavor", "flavour", "cooked",
        "menu", "sauce", "delicious", "bland", "undercooked", "overcooked",
        "fresh", "stale", "portion", "dessert", "appetizer", "entrée"
    ],
    "ambience": [
        "ambience", "atmosphere", "music", "decor", "lighting", "noise",
        "environment", "vibe", "crowded", "cozy", "dark", "bright", "noisy",
        "quiet", "layout", "smell", "odor", "odour"
    ],
    "price": [
        "price", "expensive", "cheap", "cost", "value", "overpriced",
        "affordable", "pricey", "budget", "steep", "rip-off", "deal", "discount"
    ],
    "cleanliness": [
        "clean", "dirty", "hygiene", "stain", "floor", "bathroom", "restroom",
        "table", "sanitary", "sterile", "grimy", "stains", "smudges",
        "spotless", "hygienic", "garbage", "odor"
    ],
}


def extract_aspects(text: str):
    """
    Return a list of aspects found in 'text' by matching keywords.
    If none match, return ['general'].
    """
    text_lower = text.lower()
    found = []
    for aspect, keywords in ASPECT_KEYWORDS.items():
        for kw in keywords:
            # Word‐boundary search so we don't match 'steep' inside 'steeper'
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                found.append(aspect)
                break
    return list(set(found)) if found else ["general"]


def analyze_single_review(text: str):
    """
    Runs HF pipeline on up to the first 512 chars of `text`, then extracts aspects.
    Returns a dict with keys: text, aspects (list), sentiment (str), score (float).
    """
    truncated = text[:512]
    result = SENTIMENT_PIPELINE(truncated)[0]
    aspects = extract_aspects(text)
    return {
        "text": text,
        "aspects": aspects,
        "sentiment": result["label"],  # "POSITIVE" or "NEGATIVE"
        "score": result["score"],      # confidence 0–1
    }


def batch_analyze(df, text_col="review_text", batch_size=32):
    """
    Apply `analyze_single_review` to every row in df[text_col] in batches.
    Returns a new DataFrame with added columns: 'aspects', 'sentiment', and 'score'.
    """
    records = []
    texts = df[text_col].astype(str).tolist()

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # Hugging Face sentiment pipeline can process a list:
        results = SENTIMENT_PIPELINE(batch, batch_size=batch_size)

        for idx, res in enumerate(results):
            text = batch[idx]
            aspects = extract_aspects(text)
            records.append({
                "text": text,
                "aspects": aspects,
                "sentiment": res["label"],
                "score": res["score"],
            })

    df_out = df.reset_index(drop=True).copy()
    df_out["aspects"] = [r["aspects"] for r in records]
    df_out["sentiment"] = [r["sentiment"] for r in records]
    df_out["score"] = [r["score"] for r in records]
    return df_out
