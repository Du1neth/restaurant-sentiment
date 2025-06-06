import pandas as pd
import matplotlib.pyplot as plt

def plot_negative_ratios(aspect_counts):
    """
    Generate a bar chart showing the negative sentiment ratio for each aspect.
    
    Args:
        aspect_counts (dict): Dictionary containing aspect sentiment counts
            Format: {
                "aspect_name": {"POSITIVE": count, "NEGATIVE": count},
                ...
            }
    """
    # Compute negative ratios
    aspects = list(aspect_counts.keys())
    neg_ratios = [
        aspect_counts[a]["NEGATIVE"] / (aspect_counts[a]["POSITIVE"] + aspect_counts[a]["NEGATIVE"])
        for a in aspects
    ]

    # Create bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(aspects, neg_ratios)
    plt.ylabel("Negative Ratio")
    plt.title("Negative Sentiment Ratio by Aspect")
    plt.ylim(0, 1)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example usage with the provided data
    aspect_counts = {
        "ambience": {"POSITIVE": 1719, "NEGATIVE": 1294},
        "service": {"POSITIVE": 1950, "NEGATIVE": 1644},
        "food": {"POSITIVE": 1864, "NEGATIVE": 1586},
        "price": {"POSITIVE": 551, "NEGATIVE": 604},
        "cleanliness": {"POSITIVE": 55, "NEGATIVE": 186},
    }
    
    plot_negative_ratios(aspect_counts) 