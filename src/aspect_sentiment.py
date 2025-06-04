# src/aspect_sentiment.py

import re
from transformers import pipeline

# 1) Initialize the Hugging Face sentiment pipeline once at import time
SENTIMENT_PIPELINE = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# 2) Define keyword lists for each aspect
ASPECT_KEYWORDS = {
    "service": ["service", "waiter", "server", "staff", "attentive", "rude", "slow", "friendly"],
    "food": ["food", "dish", "meal", "taste", "flavor", "cooked", "menu", "sauce", "delicious", "bland"],
    "ambience": ["ambience", "atmosphere", "music", "decor", "lighting", "noise", "environment", "vibe"],
    "price": ["price", "expensive", "cheap", "cost", "value", "overpriced", "affordable", "pricey"],
    "cleanliness": ["clean", "dirty", "hygiene", "stain", "floor", "bathroom", "restroom", "table"],
}

def extract_aspects(text: str):
    """
    Return a list of aspects found in 'text' by matching keywords.
    If no known keyword is found, returns ['general'] as a fallback.
    """
    text_lower = text.lower()
    found = []
    for aspect, keywords in ASPECT_KEYWORDS.items():
        for kw in keywords:
            # Use word-boundary to avoid partial matches
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                found.append(aspect)
                break
    return list(set(found)) if found else ["general"]

def analyze_single_review(text: str):
    """
    Runs HF sentiment pipeline on the first 512 chars, then extracts aspects.
    Returns a dict with keys: text, aspects (list), sentiment (str), score (float).
    """
    truncated = text[:512]
    result = SENTIMENT_PIPELINE(truncated)[0]
    aspects = extract_aspects(text)
    return {
        "text": text,
        "aspects": aspects,
        "sentiment": result["label"],  # "POSITIVE" or "NEGATIVE"
        "score": result["score"],
    }

def batch_analyze(df, text_col="review_text", batch_size=32):
    """
    Apply sentiment + aspect extraction to every row in df[text_col], in batches.
    Returns a new DataFrame having three additional columns:
      - aspects (list of strings)
      - sentiment ("POSITIVE"/"NEGATIVE")
      - score (float confidence)
    """
    records = []
    texts = df[text_col].astype(str).tolist()

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # HF pipeline can consume a list:
        results = SENTIMENT_PIPELINE(batch, batch_size=batch_size)

        for idx, res in enumerate(results):
            rec = {
                "text": batch[idx],
                "aspects": extract_aspects(batch[idx]),
                "sentiment": res["label"],
                "score": res["score"],
            }
            records.append(rec)

    # Build output DataFrame by reusing df’s index order
    df_out = df.reset_index(drop=True).copy()
    df_out["aspects"] = [r["aspects"] for r in records]
    df_out["sentiment"] = [r["sentiment"] for r in records]
    df_out["score"] = [r["score"] for r in records]

    return df_out
