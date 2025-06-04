# explore_data.py

import pandas as pd
from src.data_ingest import load_reviews

def main():
    # 1) Load the CSV
    df = load_reviews("data/restaurants_reviews.csv")
    total_rows = len(df)
    print(f"Total rows after dropping null review_text: {total_rows}")

    # 2) Check for empty strings
    empty_texts = df["review_text"].str.strip().eq("").sum()
    print(f"Number of rows with empty review_text (after strip): {empty_texts}")

    # 3) Check for exact duplicates (based on all columns)
    dup_full = df.duplicated().sum()
    print(f"Fully duplicate rows: {dup_full}")

    # 4) Check for duplicate review_texts
    dup_text = df["review_text"].duplicated().sum()
    print(f"Duplicate review_text values: {dup_text}")

    # 5) Show rating distribution (if rating exists)
    if "rating" in df.columns:
        print("\nRating distribution:")
        print(df["rating"].value_counts().sort_index())

    # 6) Show a few random reviews for manual inspection
    print("\n--- Sample Reviews (5 random) ---")
    print(df["review_text"].sample(5, random_state=42).to_string(index=False))

if __name__ == "__main__":
    main()
