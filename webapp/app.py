import os
from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd

# Add project root to path so we can import src modules
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_ingest import load_reviews
from src.aspect_sentiment import batch_analyze
from src.report_gen import aggregate_aspect_sentiments, generate_actionable_phrases

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"  # needed for flashing messages

# Where to store uploaded CSVs (in-memory or temp)
UPLOAD_FOLDER = os.path.join(project_root, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # limit to ~10 MB

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Renders a form where the user can upload a CSV.
    On POST, it saves the CSV, runs the pipeline, and redirects to /report.
    """
    if request.method == "POST":
        # Check if a file was submitted
        if "csv_file" not in request.files:
            flash("No file part in the request.", "error")
            return redirect(request.url)
        file = request.files["csv_file"]
        if file.filename == "":
            flash("No file selected.", "error")
            return redirect(request.url)

        # Only accept .csv
        if not file.filename.lower().endswith(".csv"):
            flash("Please upload a CSV file.", "error")
            return redirect(request.url)

        # Save uploaded file
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(save_path)

        # Redirect to the report route, passing the filename as a query parameter
        return redirect(url_for("report", filename=file.filename))

    return render_template("index.html")


@app.route("/report")
def report():
    """
    Reads the uploaded CSV (from query string), runs the sentiment pipeline,
    and renders an HTML page with the aspect summary and actionable suggestions.
    """
    filename = request.args.get("filename")
    if not filename:
        flash("No filename provided.", "error")
        return redirect(url_for("index"))

    csv_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(csv_path):
        flash(f"File '{filename}' not found on server.", "error")
        return redirect(url_for("index"))

    try:
        df = load_reviews(csv_path)
    except Exception as e:
        flash(f"Error loading CSV: {e}", "error")
        return redirect(url_for("index"))

    # Run the pipeline (you could expose min_confidence/threshold via form in the future)
    df_tagged = batch_analyze(df, text_col="review_text", batch_size=16, min_confidence=0.5)
    aspect_counts = aggregate_aspect_sentiments(df_tagged)
    suggestions = generate_actionable_phrases(aspect_counts, threshold_pct=0.3)

    # Prepare data for template
    # Convert aspect_counts to a dict of {aspect: (pos_count, neg_count)}
    summary = {
        aspect: (counts["POSITIVE"], counts["NEGATIVE"])
        for aspect, counts in aspect_counts.items()
    }

    return render_template(
        "report.html",
        total_reviews=len(df),
        summary=summary,
        suggestions=suggestions,
        filename=filename
    )

if __name__ == "__main__":
    # Run in debug mode for development; in production use a WSGI server.
    app.run(host="0.0.0.0", port=5000, debug=True)
