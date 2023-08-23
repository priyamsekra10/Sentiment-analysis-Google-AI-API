"""
At the command line, only need to run once to install the package via pip:
$ pip install google-generativeai
$ pip install json
$ pip install google-cloud-aiplatform
$ pip install pandas
$ pip install matplotlib
$ pip install time
$ pip install dotenv
"""
from json import dumps, loads
import google.generativeai as palm
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import re
from dotenv import load_dotenv
#Load API_KEY from .env file
load_dotenv()
# Google Generative AI Palm API Key
palm.configure(api_key=os.environ['API_KEY'])
# Google Generative AI Default Settings
defaults = {
  'model': 'models/text-bison-001',
  'temperature': 0.7,
  'candidate_count': 1,
  'top_k': 40,
  'top_p': 0.95,
  'max_output_tokens': 1024,
  'stop_sequences': [],
  'safety_settings': [{"category":"HARM_CATEGORY_DEROGATORY","threshold":4},{"category":"HARM_CATEGORY_TOXICITY","threshold":4},{"category":"HARM_CATEGORY_VIOLENCE","threshold":4},{"category":"HARM_CATEGORY_SEXUAL","threshold":4},{"category":"HARM_CATEGORY_MEDICAL","threshold":4},{"category":"HARM_CATEGORY_DANGEROUS","threshold":4}],
}
# Process each record
def process_and_append_added_sentiment_and_score_results_to_csv(single_record):
  # Access the value in the first row and nineth column
  Sentence = single_record.loc[single_record.index, "Summary"]
  prompt = f"""Tell me whether the following sentence's sentiment is 'positive', 'negative' or neither which would make it 'neutral'.
            Sentence {Sentence}
            Sentiment"""
  response = palm.generate_text(
    **defaults,
    prompt=prompt
  )
  response_result = re.sub('\W+','', response.result ) # returns ('positive' 'negative' or 'neutral')
  print(response_result)
   # Create a new DataFrame from the chunk
  df_single_record = pd.DataFrame(single_record)  
   # Convert the JSON string to a Pandas DataFrame 
  column_to_append = {'Sentiment': response_result}
  # Append the column to the DataFrame
  df_single_record = df_single_record.assign(**column_to_append)
  # Save the DataFrame to a CSV file
  # Get the path to the CSV file
  csv_file_path = "food_review_data_added_sentiment_added_score.csv"
  # Check if the file exists
  if not os.path.exists(csv_file_path):
  # Create the file
    with open(csv_file_path, "w") as f:
      f.write("")
  # Get the file's status
  file_status = os.stat(csv_file_path)
  # Check if header needs to be added depending on
  # existence of the file
  isHeaderRequired = False
  # Check if the file has data
  if file_status.st_size > 0:
    # The file has data. Remove header    
    isHeaderRequired = False
    # The file is empty. Header required
  else:
    isHeaderRequired = True
  # Open the CSV file in append mode
  with open(csv_file_path, "a") as csv_file:
  # Write the DataFrame to the CSV file
    df_single_record.to_csv(csv_file, index=False, header=isHeaderRequired)  
# Generates Sentiment Distribution Graph
def create_sentiment_distribution_graph():
  df_graph = pd.read_csv("food_review_data_added_sentiment_added_score.csv")
  # Get the sentiment counts
  sentiment_counts = df_graph["Sentiment"].value_counts()
  # Create a bar chart of the sentiment counts
  plt.bar(sentiment_counts.index, sentiment_counts.values)
  plt.xlabel("Sentiment")
  plt.ylabel("Count")
  plt.title("Sentiment Distribution")
  plt.show()
# Read the data into a DataFrame  
df_no_sentiment_no_score = pd.read_csv("food_review_data_no_sentiment_no_score.csv")
df_no_sentiment_no_score_filtered = df_no_sentiment_no_score[['Id', 'Summary']]
# Get the number of rows in the DataFrame
n_rows = len(df_no_sentiment_no_score_filtered)
# Iterate over every single record
# Set the chunk size
chunk_size = 1
# Iterate over chunks
for i in range(0, len(df_no_sentiment_no_score_filtered), chunk_size):
    chunk = df_no_sentiment_no_score_filtered.iloc[i:i+chunk_size]
    # Save Added Sentiment and Score Results to a CSV file
    process_and_append_added_sentiment_and_score_results_to_csv(chunk)
    # Wait for 5 seconds To Avoid Hitting API Quota
    time.sleep(5)
# Once all data has been processed we generate
# the Sentiment Distribution Graph
create_sentiment_distribution_graph()    
