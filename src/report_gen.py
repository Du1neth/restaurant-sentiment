# src/report_gen.py

from collections import defaultdict

# Templates for each aspect—include this suggestion if negative‐ratio ≥ threshold_pct
ACTIONS_TEMPLATES = {
    "service": "Consider additional staff training to improve service quality.",
    "food": "Review and enhance menu items to improve food taste and presentation.",
    "ambience": "Assess dining room environment (lighting, music) to create a more inviting atmosphere.",
    "price": "Reevaluate pricing strategy or offer promotions to deliver better perceived value.",
    "cleanliness": "Ensure regular cleaning schedules to maintain a spotless dining area.",
    "general": "Monitor overall feedback and identify common pain points."
}

def aggregate_aspect_sentiments(df):
    """
    Input: a DataFrame that must have columns:
        - 'aspects'   : a list of aspect‐strings, e.g. ['food','service']
        - 'sentiment' : either "POSITIVE" or "NEGATIVE"
    Output: a dict mapping each aspect → {"POSITIVE": int, "NEGATIVE": int}

    Example:
      If two reviews have aspects ['food','service'] with sentiments
      ["POSITIVE","NEGATIVE"], the returned dict would be:
      {
        "food":     {"POSITIVE":1,"NEGATIVE":0},
        "service":  {"POSITIVE":1,"NEGATIVE":1}
      }
    """
    aspect_counts = defaultdict(lambda: {"POSITIVE": 0, "NEGATIVE": 0})

    for _, row in df.iterrows():
        sentiment = row["sentiment"]
        # row["aspects"] is a list; loop through each aspect
        for aspect in row["aspects"]:
            aspect_counts[aspect][sentiment] += 1

    return dict(aspect_counts)

def generate_actionable_phrases(aspect_counts, threshold_pct=0.3):
    """
    Given aspect_counts (from aggregate_aspect_sentiments), return a list of suggestions.
    If (NEGATIVE / (POSITIVE + NEGATIVE)) ≥ threshold_pct for an aspect,
    include ACTIONS_TEMPLATES[aspect] in the returned list.

    If no aspect meets threshold, returns a single fallback suggestion.
    """
    suggestions = []
    for aspect, counts in aspect_counts.items():
        pos = counts.get("POSITIVE", 0)
        neg = counts.get("NEGATIVE", 0)
        total = pos + neg
        if total == 0:
            continue
        neg_ratio = neg / total
        if neg_ratio >= threshold_pct:
            tmpl = ACTIONS_TEMPLATES.get(aspect)
            if tmpl:
                suggestions.append(tmpl)

    if not suggestions:
        suggestions.append(
            "No major negative trends detected—consider gathering more feedback for deeper analysis."
        )
    return suggestions
