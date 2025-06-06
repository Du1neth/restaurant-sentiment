# test_report_gen.py

import pandas as pd
from src.data_ingest import load_reviews
from src.aspect_sentiment import batch_analyze
from src.report_gen import aggregate_aspect_sentiments, generate_actionable_phrases

def main():
    # 1) Load the first 50 reviews for a quick test
    df_full = load_reviews("data/restaurants_reviews.csv")
    df_small = df_full

    # 2) Tag each row with aspects + sentiment (batch in size 16 for speed)
    df_tagged = batch_analyze(df_small, text_col="review_text", batch_size=16)

    # 3) Aggregate counts by aspect
    aspect_counts = aggregate_aspect_sentiments(df_tagged)

    # 4) Print out the raw counts per aspect
    print("\n=== Aspect Sentiment Counts ===")
    for aspect, counts in aspect_counts.items():
        pos = counts.get("POSITIVE", 0)
        neg = counts.get("NEGATIVE", 0)
        total = pos + neg
        neg_ratio = neg / total if total > 0 else 0
        print(f"- {aspect:12s} → {pos} positive, {neg} negative  (neg_ratio={neg_ratio:.2f})")

        suggestions = generate_actionable_phrases(aspect_counts, threshold_pct=0.4)


    # 6) Print the suggestions
    print("\n=== Actionable Suggestions (threshold=0.3) ===")
    for idx, s in enumerate(suggestions, 1):
        print(f"{idx}. {s}")

if __name__ == "__main__":
    main()
