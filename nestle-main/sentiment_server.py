from flask import Flask, jsonify, render_template
from apify_client import ApifyClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import pandas as pd
import random
import matplotlib.pyplot as plt
from azure.ai.textanalytics import DocumentError

app = Flask(__name__)

# Initialize ApifyClient and TextAnalyticsClient with your credentials
client = ApifyClient(
    "apify_api_161VWbPtMkCidsrmli8TCbD65qJOlt45tH36"  # Replace with your actual token
)

azure_endpoint = "https://nestleanalysis.cognitiveservices.azure.com/"
azure_api_key = "2lOmejx1yLk6eRrafw4x6zz8hrY6Svxoksk1vYPCitRgBSgVbRX9JQQJ99AKACYeBjFXJ3w3AAAaACOGX3EP"

text_analytics_client = TextAnalyticsClient(
    endpoint=azure_endpoint, credential=AzureKeyCredential(azure_api_key)
)

nestle_brands = [
    "nescafe",
    "kitkat",
    "nestea",
    "nescafedolcegusto",
    "milo",
    "maggi",
    "gerber",
    "purina",
    "smarties",
    "nestletollhouse"
]

def fetch_and_analyze_sentiment():
    # Apify settings to retrieve social media posts


# Loop through the brands and construct the run_input for each brand
    for brand in nestle_brands:
        instagram_url = f"https://www.instagram.com/{brand}/"  # Construct Instagram URL for each brand
        run_input = {
            "directUrls": [instagram_url],
            "resultsType": "posts",
            "resultsLimit": 2,
            "searchType": "hashtag",
            "searchLimit": 1,
            "addParentData": False,
        }

    # Run Apify Actor to get data
    run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)
    items = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]

    # Extract comments
    comments = []
    for post in items:
        brand = post["inputUrl"].split("/")[-2]
        if "latestComments" in post:
            for comment in post["latestComments"]:
                # Only include comments with non-empty text
                if comment["text"].strip():
                    comment_data = {"text": comment["text"], "brand": brand}
                    comments.append(comment_data)

    # Perform sentiment analysis on comments in batches of 10
    batch_size = 10
    for i in range(0, len(comments), batch_size):
        batch = comments[i: i + batch_size]  # Slice the batch of up to 10 comments
        texts = [comment["text"] for comment in batch]
        
        # Try-except to handle errors from the Azure API
        try:
            response = text_analytics_client.analyze_sentiment(texts)
            for j, sentiment in enumerate(response):
                if isinstance(sentiment, DocumentError):
                    # Skip comments that result in a DocumentError
                    print(f"Error processing document {texts[j]}: {sentiment.error}")
                    continue

                # Add confidence scores and determine sentiment based on the highest score
                positive_confidence = sentiment.confidence_scores.positive
                neutral_confidence = sentiment.confidence_scores.neutral
                negative_confidence = sentiment.confidence_scores.negative

                # Classify the sentiment based on the highest confidence score
                if positive_confidence > neutral_confidence and positive_confidence > negative_confidence:
                    batch[j]["sentiment"] = "positive"
                elif negative_confidence > neutral_confidence and negative_confidence > positive_confidence:
                    batch[j]["sentiment"] = "negative"
                else:
                    batch[j]["sentiment"] = "neutral"

                batch[j]["confidence_scores"] = {
                    "positive": positive_confidence,
                    "neutral": neutral_confidence,
                    "negative": negative_confidence,
                }
        except Exception as e:
            print(f"An error occurred during sentiment analysis: {e}")

    # Ensure 'sentiment' column exists before accessing
    sentiment_df = pd.DataFrame(comments)

    # Safeguard: if 'sentiment' column is missing, default all to 'neutral'
    if 'sentiment' not in sentiment_df.columns:
        sentiment_df['sentiment'] = 'neutral'

    sentiment_counts = sentiment_df["sentiment"].value_counts().to_dict()

    total_comments = len(comments)
    
    # Calculate the raw sentiment counts
    positive_count = sentiment_counts.get("positive", 0)
    neutral_count = sentiment_counts.get("neutral", 0)
    negative_count = sentiment_counts.get("negative", 0)

    # Calculate sentiment percentages
    positive_percentage = round(positive_count / total_comments * 100)
    neutral_percentage = round(neutral_count / total_comments * 100)
    negative_percentage = round(negative_count / total_comments * 100)

    # Adjust the percentages if they do not add up to 100
    total_percentage = positive_percentage + neutral_percentage + negative_percentage
    if total_percentage != 100:
        difference = 100 - total_percentage
        # Add the difference to the category with the highest count
        if positive_count >= neutral_count and positive_count >= negative_count:
            positive_percentage += difference
        elif neutral_count >= positive_count and neutral_count >= negative_count:
            neutral_percentage += difference
        else:
            negative_percentage += difference

    # Determine the overall sentiment classification
    if neutral_count > positive_count and neutral_count > negative_count:
        overall_sentiment = "NEUTRAL"
    elif positive_count > negative_count:
        overall_sentiment = "POSITIVE"
    elif negative_count > positive_count:
        overall_sentiment = "NEGATIVE"
    else:
        # If there's a tie between positive and negative, check if neutral sentiment exists
        if neutral_count > 0:
            overall_sentiment = "NEUTRAL"
        else:
            overall_sentiment = "POSITIVE"  # Default to positive if there's no neutral sentiment

    # Pick 5 random comments
    random_comments = random.sample(comments, min(5, len(comments)))


    return {
        "overallSentiment": overall_sentiment,
        "positiveScore": positive_percentage,
        "neutralScore": neutral_percentage,
        "negativeScore": negative_percentage,
        "randomComments": random_comments,
        "trend": comments,
    }


# Endpoint to fetch sentiment data
@app.route("/sentiment-data", methods=["GET"])
def sentiment_data():
    data = fetch_and_analyze_sentiment()
    return jsonify(data)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5000)
