# Restaurant Sentiment → Actionable Report

**Overview**  
This project ingests a CSV of restaurant reviews and produces a brief “actionable improvement” report by:
1. Running a Hugging Face transformer to get sentiment for each review.
2. Extracting simple keyword‐based aspects (food, service, ambience, price, cleanliness).
3. Aggregating positive vs. negative counts per aspect.
4. Emitting a short list of suggestions (e.g., “Improve staff training,” “Revise menu items,” etc.).

**Folder Structure**  
