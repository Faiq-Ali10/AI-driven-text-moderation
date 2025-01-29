from flask import Flask, render_template, request
import re
import nltk
nltk.download('punkt_tab')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob

# Download required NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

# Simple rules-based functions for detecting violations
def detect_spam(message):
    spam_keywords = ["free", "buy now", "limited time", "click here", "win", "hurry", "offer"]
    words = word_tokenize(message.lower())
    spam_score = sum(1 for word in words if word in spam_keywords)
    return spam_score > 1  # Flag as spam if multiple spammy words are found

def detect_hate_speech(message):
    negative_words = ["hate", "stupid", "kill", "racist", "disgusting"]
    words = word_tokenize(message.lower())
    hate_score = sum(1 for word in words if word in negative_words)
    sentiment = TextBlob(message).sentiment.polarity  # Negative sentiment is closer to -1
    return hate_score > 0 or sentiment < -0.5  # Flag if toxic words exist or sentiment is very negative

def detect_personal_info(message):
    if re.search(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', message):  # Phone numbers
        return True
    if re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', message):  # Email addresses
        return True
    if re.search(r'\b\d{1,3} [A-Za-z]+ (Street|Ave|Boulevard|Road|Lane|Drive)\b', message):  # Addresses
        return True
    return False

def detect_relevance(message):
    relevant_keywords = ["AI", "technology", "software", "data", "business"]
    words = word_tokenize(message.lower())
    relevance_score = sum(1 for word in words if word in relevant_keywords)
    return relevance_score == 0  # Flag if no relevant keywords are found

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        message = request.form["message"]
        selected_guidelines = request.form.getlist("guidelines")

        flag_reasons = []
        
        if "spam" in selected_guidelines and detect_spam(message):
            flag_reasons.append("Spam detected")
        if "hate_speech" in selected_guidelines and detect_hate_speech(message):
            flag_reasons.append("Hate speech detected")
        if "personal_info" in selected_guidelines and detect_personal_info(message):
            flag_reasons.append("Personal information detected")
        if "relevance" in selected_guidelines and detect_relevance(message):
            flag_reasons.append("Message is not relevant to the brand")

        if flag_reasons:
            result = f"❌ Message flagged: {', '.join(flag_reasons)}"
        else:
            result = "✅ Message approved"

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
