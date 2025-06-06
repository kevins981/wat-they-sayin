import json
import sys
from datetime import datetime
import openai
from dotenv import load_dotenv
import os
import time
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

class ReviewExtraction(BaseModel):
    sentiment: str
    complaints: str
    approval: str
    feature_request: str

def analyze_text(text):
    """Analyze text using OpenAI API with structured output"""
    if not text.strip():
        return None
        
    try:
        response = openai.responses.parse(
            model="gpt-4o-mini",
            instructions="""Analyze the text and provide a structured analysis of opinions about the product. 
            Return a JSON object with the following fields:
            - sentiment: Overall sentiment (positive/negative/neutral)
            - complaints: Summary of any complaints or issues mentioned (leave empty if none)
            - approval: Summary of any positive feedback or approvals (leave empty if none)
            - feature_request: Summary of any feature requests or suggestions (leave empty if none)
            
            Only include fields that are present in the text. If a category is not mentioned, leave it as an empty string.
            Keep summaries concise and focused on the product-related content.""",
            text_format=ReviewExtraction,
            input=f"{text}"
        )
        
        # Parse the response as JSON
        # try:
        #     analysis = json.loads(response.output_text)
        #     return analysis
        # except json.JSONDecodeError:
        #     print("Error: Could not parse AI response as JSON")
        #     return None
        output = response.output_parsed
        # print(output)
        return output

            
    except Exception as e:
        print(f"Error analyzing text: {str(e)}")
        return None

def read_reddit_data(filename):
    """Read and parse the Reddit JSON data file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{filename}' is not a valid JSON file.")
        sys.exit(1)

def print_analysis(analysis):
    """Print the structured analysis in a readable format"""
    if not analysis:
        return
        
    print("\nAnalysis:")
    print("-"*40)
    print(analysis)

def print_post_and_comments(data):
    """Print the content of each post and its comments with AI analysis"""
    for i, post in enumerate(data, 1):
        print("\n" + "="*80)
        print(f"POST #{i}")
        print(f"Title: {post['title']}")
        print(f"Posted in: r/{post['subreddit']}")
        print(f"Posted by: u/{post['author']}")
        print(f"Posted at: {datetime.fromtimestamp(post['created_utc'])}")
        
        # Analyze post content if not empty
        if post['text'].strip():
            print("\nPost Content:")
            print("-"*40)
            print(post['text'])
            print("-"*40)
            
            analysis = analyze_text(post['text'])
            print_analysis(analysis)
        
        if post['comments']:
            print(f"\nComments ({len(post['comments'])}):")
            for j, comment in enumerate(post['comments'], 1):
                if not comment['body'].strip():
                    continue
                    
                print(f"\nComment #{j}")
                print(f"By: u/{comment['author']}")
                print(f"At: {datetime.fromtimestamp(comment['created_utc'])}")
                print(f"Score: {comment['score']}")
                print(f"Depth: {comment['depth']}")
                
                print("\nComment Content:")
                print("-"*40)
                print(comment['body'])
                print("-"*40)
                
                analysis = analyze_text(comment['body'])
                print_analysis(analysis)
                
                # Add a small delay to avoid hitting API rate limits
                time.sleep(0.5)
        else:
            print("\nNo comments on this post.")
        
        print("="*80)

def main():
    if len(sys.argv) != 2:
        print("Usage: python read_reddit_data.py <json_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    print(f"Reading data from {filename}...")
    
    data = read_reddit_data(filename)
    print(f"Found {len(data)} posts.")
    
    print_post_and_comments(data)

if __name__ == "__main__":
    main() 