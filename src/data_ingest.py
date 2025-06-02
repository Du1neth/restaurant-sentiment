# src/data_ingest.py

import pandas as pd

def load_reviews(path: str) -> pd.DataFrame:
    """
    Load a CSV of restaurant reviews. Expects a column 'review_text'.
    Returns a DataFrame with at least 'review_text'.
    Raises ValueError if 'review_text' is missing.
    """
    # 1) Read the CSV from the given path
    df = pd.read_csv(path)

    # 2) Ensure 'review_text' column exists
    if "review_text" not in df.columns:
        raise ValueError("CSV must contain a 'review_text' column.")

    # 3) Drop any rows where 'review_text' is NaN or empty
    df = df.dropna(subset=["review_text"]).reset_index(drop=True)

    # 4) (Optional) You could strip leading/trailing whitespace:
    df["review_text"] = df["review_text"].astype(str).str.strip()

    return df
