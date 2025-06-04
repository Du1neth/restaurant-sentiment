import re
from transformers import pipeline

# RoBERTa ABSA pipeline—aggregates contiguous tokens automatically
ABSA_PIPELINE = pipeline(
    "token-classification",
    model="gauneg/roberta-base-absa-ate-sentiment",
    aggregation_strategy="simple",
    device=-1  # CPU; change to 0 for GPU if available
)

def _split_label(raw_label: str):
    """
    Given something like "Food-Positive", "Food_Positive", or "FoodPositive",
    return (aspect, polarity). If no clear polarity, return (aspect, "neutral").
    """
    if "-" in raw_label:
        parts = raw_label.split("-")
    elif "_" in raw_label:
        parts = raw_label.split("_")
    else:
        parts = re.findall(r"[A-Z][a-z]*", raw_label)

    if len(parts) < 2:
        return raw_label.lower(), "neutral"
    return parts[0].lower(), parts[1].lower()

def analyze_single_review(text: str):
    """
    Run the RoBERTa ABSA model on `text` (up to 512 chars).
    Returns a dict:
      - text      : original review
      - aspects   : list of aspect strings (lowercased)
      - sentiment : "POSITIVE" or "NEGATIVE"
      - score     : float confidence of chosen polarity
    """
    snippet = text[:512]
    results = ABSA_PIPELINE(snippet)

    aspects_set = set()
    neg_confidences = []
    pos_confidences = []

    for item in results:
        raw_label = item.get("entity_group", "")
        confidence = float(item.get("score", 0.0))

        asp, pol = _split_label(raw_label)
        aspects_set.add(asp)

        if pol == "negative":
            neg_confidences.append(confidence)
        else:
            # "positive" or "neutral"
            pos_confidences.append(confidence)

    if neg_confidences:
        overall_sentiment = "NEGATIVE"
        overall_score = max(neg_confidences)
    elif pos_confidences:
        overall_sentiment = "POSITIVE"
        overall_score = max(pos_confidences)
    else:
        overall_sentiment = "POSITIVE"
        overall_score = 0.0

    final_aspects = list(aspects_set) if aspects_set else ["general"]

    return {
        "text": text,
        "aspects": final_aspects,
        "sentiment": overall_sentiment,
        "score": overall_score
    }

def batch_analyze(df, text_col="review_text", batch_size=16):
    """
    Applies analyze_single_review logic to each row in df[text_col].
    Returns a new DataFrame with added columns: 'aspects', 'sentiment', 'score'.
    """
    import pandas as pd

    records = []
    texts = df[text_col].astype(str).tolist()

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_entities = ABSA_PIPELINE(batch_texts)

        # If HF version returns a flat list (not a list-of-lists), regroup by 'index'
        if not isinstance(batch_entities[0], list):
            grouped = []
            temp = []
            curr_idx = batch_entities[0]["index"]
            for ent in batch_entities:
                if ent["index"] != curr_idx:
                    grouped.append(temp)
                    temp = []
                    curr_idx = ent["index"]
                temp.append(ent)
            grouped.append(temp)
            batch_entities = grouped

        # Now batch_entities[j] is the list of entity dicts for batch_texts[j]
        for j, entity_list in enumerate(batch_entities):
            text = batch_texts[j]
            aspects_set = set()
            neg_conf = []
            pos_conf = []

            for item in entity_list:
                raw_label = item.get("entity_group", "")
                confidence = float(item.get("score", 0.0))
                asp, pol = _split_label(raw_label)
                aspects_set.add(asp)
                if pol == "negative":
                    neg_conf.append(confidence)
                else:
                    pos_conf.append(confidence)

            if neg_conf:
                overall_s = "NEGATIVE"
                overall_sc = max(neg_conf)
            elif pos_conf:
                overall_s = "POSITIVE"
                overall_sc = max(pos_conf)
            else:
                overall_s = "POSITIVE"
                overall_sc = 0.0

            final_aspects = list(aspects_set) if aspects_set else ["general"]

            records.append({
                "text": text,
                "aspects": final_aspects,
                "sentiment": overall_s,
                "score": overall_sc
            })

    df_out = df.reset_index(drop=True).copy()
    df_out["aspects"] = [r["aspects"] for r in records]
    df_out["sentiment"] = [r["sentiment"] for r in records]
    df_out["score"] = [r["score"] for r in records]
    return df_out
