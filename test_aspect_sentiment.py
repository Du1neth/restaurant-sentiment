# test_aspect_sentiment.py

import pandas as pd
from src.data_ingest import load_reviews
from src.aspect_sentiment import analyze_single_review, batch_analyze

def main():
    samples = [
        "The food was delicious but service was slow.",
        "Great ambience, lively music, but the waiter was rude.",
        "Pricey but worth it for the taste.",
        "Tables were dirty and bathrooms unclean.",
        "Just an average visit—nothing special to mention."
    ]
    print("=== analyze_single_review() Tests (min_confidence=0.70) ===")
    for s in samples:
        res = analyze_single_review(s, min_confidence=0.70)
        print(f"\nText: {s}")
        print(f"  Aspects: {res['aspects']} | Sentiment: {res['sentiment']} | Score: {res['score']:.2f}")

    print("\n=== Running batch_analyze on 20 real reviews (min_confidence=0.70) ===")
    df = load_reviews("data/restaurants_reviews.csv")
    df_small = df.head(20)
    df_tagged = batch_analyze(df_small, text_col="review_text", batch_size=8, min_confidence=0.70)
    print(df_tagged[["review_text", "aspects", "sentiment", "score"]].head(5).to_string(index=False))

if __name__ == "__main__":
    main()
