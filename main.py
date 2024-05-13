# Import necessary modules and libraries
from json import dumps, loads
import google.generativeai as palm
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI Palm API with API key
palm.configure(api_key=os.environ['API_KEY'])

# Define default settings for text generation model
defaults = {
    'model': 'models/text-bison-001',
    'temperature': 0.7,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024,
    'stop_sequences': [],
    'safety_settings': [
        {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 4},
        {"category": "HARM_CATEGORY_TOXICITY", "threshold": 4},
        {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 4},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 4},
        {"category": "HARM_CATEGORY_MEDICAL", "threshold": 4},
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 4},
    ],
}

# Process each record, generate summary, and append to CSV
# Process each record, generate summary, and append to CSV
def process_and_append_summary_to_csv(single_record):
    # Access the text data from the 'Text' column directly
    sentence = single_record["Text"]
    
    # Prompt to generate summary
    prompt = f"""Summarize the following sentence in 6-8 words:
              {sentence}"""
    
    # Generate summary
    response = palm.generate_text(
        **defaults,
        prompt=prompt
    )
    summary = response.result.strip()
    
    # Save ID and summary to a separate CSV file
    summary_data = pd.DataFrame({'Id': single_record['Id'], 'Summary': summary}, index=[0])
    summary_csv_file = "sentence_summary.csv"
    summary_data.to_csv(summary_csv_file, mode='a', index=False, header=not os.path.exists(summary_csv_file))


# Analyze sentiment of the generated summaries
def analyze_sentiment_of_summaries():
    # Read summaries from CSV file
    summary_data = pd.read_csv("sentence_summary.csv")
    
    for index, row in summary_data.iterrows():
        summary = row['Summary']
        
        # Prompt to analyze sentiment of summary
        # prompt = f"""Analyze the sentiment of the following summary:
        #           {summary}"""
        
        prompt = f"""I will provide you a sentance at a time. You have to analyze the sentiment fo the user and only return back the score of positivity. The score can be anywhere between 0 to 100. 100 for very positive, 0 for negitive.
            Sentence {summary}
            Sentiment score"""
        
        # Generate sentiment score
        response = palm.generate_text(
            **defaults,
            prompt=prompt
        )
        sentiment_score = response.result.strip()
        
        # Update summary CSV with sentiment score
        summary_data.at[index, 'Sentiment'] = sentiment_score
        
    # Save updated summary data
    summary_data.to_csv("sentence_summary.csv", index=False)

# Main execution
# Main execution
if __name__ == "__main__":
    # Read the data into a DataFrame
    df_no_sentiment_no_score = pd.read_csv("/home/priyam/DATA 2/Quibble AI/Sentiment analysis/generative-ai-sentiment-analysis/food_review_data_no_sentiment_no_score.csv")
    
    # Iterate over each record
    for index, row in df_no_sentiment_no_score.iterrows():
        # Process and append summary to CSV
        process_and_append_summary_to_csv(row)
        
        # Analyze sentiment of the generated summary
        analyze_sentiment_of_summaries()
        
        # Wait for 5 seconds to avoid API quota issues
        time.sleep(5)
