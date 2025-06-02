# test_data_ingest.py

from src.data_ingest import load_reviews

if __name__ == "__main__":
    # Adjust the path if needed; this assumes your CSV is at data\restaurants_reviews.csv
    csv_path = "data/restaurants_reviews.csv"

    print(f"Loading CSV from: {csv_path}")
    df = load_reviews(csv_path)
    print(f"Successfully loaded {len(df)} rows.")

    # Print the first 5 rows to confirm 'review_text' is loaded
    print("\n--- Sample Rows ---")
    print(df["review_text"].head(5).to_string(index=False))
