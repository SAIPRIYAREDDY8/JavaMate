from flask import Flask, render_template, request, jsonify
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib

app = Flask(__name__)

# =========================
# LOAD DATASET
# =========================
with open("qa_data.json", "r") as f:
    data = json.load(f)

questions = [item["question"] for item in data]
answers = [item["answer"] for item in data]

# Build keyword list for spell correction
keywords = list(set(" ".join(questions).lower().split()))

# =========================
# NLP MODEL (TF-IDF)
# =========================
vectorizer = TfidfVectorizer()
question_vectors = vectorizer.fit_transform(questions)

# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# SEARCH API
# =========================
@app.route("/search", methods=["POST"])
def search():
    user_query = request.json["query"].lower()

    # -------------------------
    # SPELL CORRECTION
    # -------------------------
    words = user_query.split()
    corrected_words = []

    for w in words:
        match = difflib.get_close_matches(w, keywords, n=1, cutoff=0.7)
        corrected_words.append(match[0] if match else w)

    corrected_query = " ".join(corrected_words)

    suggestion = ""
    if corrected_query != user_query:
        suggestion = f"Did you mean: {corrected_query}?"

    # -------------------------
    # SEARCH MATCHING
    # -------------------------
    query_vec = vectorizer.transform([corrected_query])
    similarity = cosine_similarity(query_vec, question_vectors)

    best_index = similarity.argmax()
    best_score = similarity[0][best_index]

    # Threshold for no result
    if best_score < 0.2:
        answer = "No relevant answer found in Java database."
    else:
        answer = answers[best_index]

    return jsonify({
        "answer": answer,
        "suggestion": suggestion
    })

# =========================
# AUTO SUGGESTIONS API
# =========================
@app.route("/suggest")
def suggest():
    query = request.args.get("q", "").lower()

    suggestions = []

    for q in questions:
        if query in q.lower():
            suggestions.append(q)

    return jsonify(suggestions[:5])

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)