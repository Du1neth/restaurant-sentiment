# src/main.py

import argparse
import pandas as pd
from src.data_ingest import load_reviews
from src.aspect_sentiment import batch_analyze
from src.report_gen import aggregate_aspect_sentiments, generate_actionable_phrases

def main(args):
    df = load_reviews(args.input)
    total_reviews = len(df)

    print(f"\nLoaded {total_reviews} reviews from '{args.input}'.\n")

    print(f"Analyzing {total_reviews} reviews (batch size={args.batch_size}, min_confidence={args.min_confidence})…")
    df_tagged = batch_analyze(
        df,
        text_col="review_text",
        batch_size=args.batch_size,
        min_confidence=args.min_confidence
    )
    print("Done.\n")

    aspect_counts = aggregate_aspect_sentiments(df_tagged)

    print("=== Aspect Sentiment Summary ===")
    for aspect, counts in aspect_counts.items():
        pos = counts.get("POSITIVE", 0)
        neg = counts.get("NEGATIVE", 0)
        total = pos + neg
        neg_ratio = neg / total if total > 0 else 0.0
        print(f"- {aspect:12s}: {pos} positive, {neg} negative  (neg_ratio={neg_ratio:.2f})")
    print()

    suggestions = generate_actionable_phrases(aspect_counts, threshold_pct=args.threshold)

    print(f"=== Actionable Suggestions (threshold={args.threshold}) ===\n")
    for i, s in enumerate(suggestions, 1):
        print(f"{i}. {s}")
    print()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fout:
            fout.write("Actionable Improvement Suggestions:\n\n")
            for i, s in enumerate(suggestions, 1):
                fout.write(f"{i}. {s}\n")
        print(f"Saved text report to: {args.output}\n")

    if args.html:
        from jinja2 import Environment, FileSystemLoader

        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("report.html.j2")
        aspect_series = {
            asp: pd.Series(cnts) for asp, cnts in aspect_counts.items()
        }
        rendered = template.render(
            total_reviews=total_reviews,
            aspect_counts=aspect_series,
            suggestions=suggestions
        )
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(rendered)
        print(f"Saved HTML report to: {args.html}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CSV of reviews → actionable suggestions (with optional confidence filtering)"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input CSV (must have 'review_text' column)."
    )
    parser.add_argument(
        "--output", "-o",
        help="(Optional) Path to save plain-text report."
    )
    parser.add_argument(
        "--html",
        help="(Optional) Path to save HTML report (requires Jinja2 template)."
    )
    parser.add_argument(
        "--threshold", "-t", type=float, default=0.3,
        help="Negative-ratio threshold for suggestions (default: 0.3)."
    )
    parser.add_argument(
        "--batch_size", "-b", type=int, default=16,
        help="Batch size for the sentiment pipeline (default: 16)."
    )
    parser.add_argument(
        "--min_confidence", "-c", type=float, default=0.0,
        help="Minimum confidence (0–1) to trust an aspect-sentiment (default: 0.0)."
    )
    args = parser.parse_args()
    main(args)
