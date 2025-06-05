# src/aspect_sentiment.py

import re
from transformers import pipeline

# Initialize once at import time
SENTIMENT_PIPELINE = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

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
    Keyword‐based aspect extraction. If no match, returns ['general'].
    """
    text_lower = text.lower()
    found = []
    for aspect, keywords in ASPECT_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                found.append(aspect)
                break
    return list(set(found)) if found else ["general"]

def analyze_single_review(text: str, min_confidence: float = 0.0):
    """
    Run HF sentiment pipeline over up to 512 chars of `text`, then extract aspects.
    Only keep sentiment if its confidence ≥ min_confidence.
    Returns a dict: {
      'text': str,
      'aspects': List[str],
      'sentiment': "POSITIVE" or "NEGATIVE",
      'score': float
    }
    """
    truncated = text[:512]
    result = SENTIMENT_PIPELINE(truncated)[0]
    raw_label = result["label"]           # "POSITIVE" or "NEGATIVE"
    raw_score = float(result["score"])    # confidence

    # If the model isn’t confident enough, treat as “neutral” → always positive
    if raw_score < min_confidence:
        aspects = ["general"]
        overall_sentiment = "POSITIVE"
        overall_score = raw_score
    else:
        aspects = extract_aspects(text)
        overall_sentiment = raw_label
        overall_score = raw_score

    return {
        "text": text,
        "aspects": aspects,
        "sentiment": overall_sentiment,
        "score": overall_score
    }

def batch_analyze(df, text_col="review_text", batch_size=32, min_confidence: float = 0.0):
    """
    Apply `analyze_single_review` to every row in df[text_col] with batching.
    Returns a new DataFrame with added columns: 'aspects', 'sentiment', 'score'.
    """
    import pandas as pd

    records = []
    texts = df[text_col].astype(str).tolist()

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        results = SENTIMENT_PIPELINE(batch, batch_size=batch_size)

        for idx, res in enumerate(results):
            text = batch[idx]
            label = res["label"]
            score = float(res["score"])

            if score < min_confidence:
                # If confidence too low, fallback to general/positive
                aspects = ["general"]
                sentiment = "POSITIVE"
                final_score = score
            else:
                aspects = extract_aspects(text)
                sentiment = label
                final_score = score

            records.append({
                "text": text,
                "aspects": aspects,
                "sentiment": sentiment,
                "score": final_score
            })

    df_out = df.reset_index(drop=True).copy()
    df_out["aspects"] = [r["aspects"] for r in records]
    df_out["sentiment"] = [r["sentiment"] for r in records]
    df_out["score"] = [r["score"] for r in records]
    return df_out
