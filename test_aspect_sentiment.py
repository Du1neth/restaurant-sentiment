# test_aspect_sentiment.py

import pandas as pd
from src.data_ingest import load_reviews
from src.aspect_sentiment import analyze_single_review, batch_analyze

def main():
    # 1) Quick manual sanity checks
    samples = [
        "The food was delicious but service was slow.",
        "Great ambience, lively music, but the waiter was rude.",
        "Pricey but worth it for the taste.",
        "Tables were dirty and bathrooms unclean.",
        "Just an average visit—nothing special to mention."
    ]
    print("=== analyze_single_review() Tests ===")
    for s in samples:
        res = analyze_single_review(s)
        print(f"\nText: {s}")
        print(f"  Aspects: {res['aspects']} | Sentiment: {res['sentiment']} | Score: {res['score']:.2f}")

    # 2) Batch analyze first 20 real reviews
    print("\n=== Running batch_analyze on 20 real reviews ===")
    df = load_reviews("data/restaurants_reviews.csv")
    df_small = df.head(20)
    df_tagged = batch_analyze(df_small, text_col="review_text", batch_size=8)

    print(df_tagged[["review_text", "aspects", "sentiment", "score"]].head(5).to_string(index=False))

if __name__ == "__main__":
    main()
