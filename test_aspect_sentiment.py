# test_aspect_sentiment.py

import pandas as pd
from src.data_ingest import load_reviews
from src.aspect_sentiment import extract_aspects, batch_analyze

def main():
    # 1) Load just the first 20 rows so the test runs quickly
    df_full = load_reviews("data/restaurants_reviews.csv")
    df_small = df_full.head(20)

    # 2) Test extract_aspects on a few handcrafted examples
    samples = [
        "The food was delicious but service was slow.",
        "Great ambience, lovely music, and friendly staff.",
        "Pricey but worth it for the taste.",
        "Tables were dirty and bathrooms unclean.",
        "Just an average visit—nothing special to mention."
    ]
    print("=== extract_aspects() Tests ===")
    for s in samples:
        print(f"Review: \"{s}\"")
        print("  Aspects found:", extract_aspects(s))
    print()

    # 3) Run full batch_analyze on df_small
    print("=== Running batch_analyze on 20 real reviews ===")
    df_tagged = batch_analyze(df_small, text_col="review_text", batch_size=8)

    # 4) Print the first 5 rows with new columns
    subset = df_tagged[["review_text", "aspects", "sentiment", "score"]].head(5)
    print(subset.to_string(index=False))

if __name__ == "__main__":
    main()
