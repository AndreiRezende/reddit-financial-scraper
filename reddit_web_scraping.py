import praw
from pymongo import MongoClient, errors
import pymongo
from datetime import datetime, timezone, timedelta
import spacy
from collections import Counter
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv() # Load .env variables

# Load a pre-trained Portuguese language model for NLP
# 'pt_core_news_lg' is a large model for the Portuguese language
nlp = spacy.load('pt_core_news_lg')

# Read environment variables - Reddit API Setup
id_reddit =  os.environ.get('ID_REDDIT')
secret_reddit = os.environ.get('SECRET_REDDIT')
password_reddit = os.environ.get('PASSWORD_REDDIT')
user_agent = os.environ.get("USER_AGENT")
username_reddit = os.environ.get('USERNAME_REDDIT')

# Create an authenticated Reddit instance
reddit = praw.Reddit(
    client_id=id_reddit,
    client_secret=secret_reddit,
    password=password_reddit,
    user_agent=user_agent,
    username=username_reddit,
)

# Read environment variables - MongoDB Connection
connection_string_mongo = os.environ.get('MONGODB_URI')
database_mongo = os.environ.get("DATABASE_MONGODB")
collection_mongo = os.environ.get("COLLECTION_MONGODB")

# Accessing the database and collection 
client = MongoClient(connection_string_mongo)
db = client[database_mongo]
collection = db[collection_mongo]
collection.create_index([('id', pymongo.ASCENDING)], unique=True)


tickers = ['PETR4', 'PRIO3', 'VBBR3', 'RRRP3', 'CSAN3', 'VALE3', 'GGBR4', 'SUZB3', 'CSNA3', 'USIM5', 'GOAU4', 'MGLU3', 'RENT3', 'LREN3', 'AMER3', 'VIIA3', 'LCAM3', 'ITUB4', 'BBDC4', 'B3SA3', 'BBAS3', 'BPAC11', 'ITSA4', 'bbse3']
corporations = ['Petrobras', 'PetroRio', 'Vibra Energia', '3R Petroleum', 'Cosan', 'Vale SA', 'Gerdau', 'Suzano SA', 'CSN', 'Usiminas', 'Metalúrgica Gerdau', 'Magazine Luiza', 'Localiza', 'Lojas Renner', 'Americanas SA', 'Via Varejo', 'Locamerica', 'Itaú Unibanco', 'Bradesco', 'B3 SA', 'Banco do Brasil', 'BTG Pactual', 'Itaúsa']

# Search Parameters for the scraper
subreddit_name = "investimentos"
subreddit = reddit.subreddit(subreddit_name)
terms = tickers + corporations
time_filter_reddit = "day"


# Function to check if a comment body contains any of the predefined search terms
def contains_keywords(comment_body, terms):
    return any(term.lower() in comment_body.lower() for term in terms)

# Function to scrape and process a single Reddit post
def process_and_save_post(post):
    print(f"Title: {post.title}, Score: {post.score}, URL: {post.url}")
    print("\n")

    # Define the Brasília timezone (UTC-3)
    brasilia_timezone = timezone(timedelta(hours=-3))

    # Converts the post's creation timestamp (UTC) into a timezone-aware datetime object
    utc_datetime = datetime.fromtimestamp(post.created_utc, timezone.utc)

    # Converts the UTC datetime to the Brasília timezone for local reference
    created_datetime_brasilia = utc_datetime.astimezone(brasilia_timezone)
    
    print(created_datetime_brasilia)

    # Gets the author's username or marks it as '[deleted]' if unavailable
    author_name = post.author.name if post.author else '[deleted]'
    print(f"Author: {author_name}")

    # Uses the SpaCy NLP model to process the post's main text
    tokens = nlp(post.selftext)

    # A list to store the processed tokens and their attributes
    content = []

    # Iterates through each token to extract key NLP features
    for token in tokens:
        # Skips stop words (common words in PT-BR, like 'a', 'o') and punctuation
        if not (token.is_stop or token.is_punct):
            # Creates a dictionary with token details (text, part-of-speech tag, dependency parsing, and lemma)
            pipeline_tokens = {
                "token": token.text,
                "tagging": token.pos_,
                "parsing": token.dep_,
                "lemmatization": token.lemma_
            }

            # Adds the processed token to the list
            content.append(pipeline_tokens)

    # Extracts named entities (companies, people) and their labels from the text
    entities = [(ent.text, ent.label_) for ent in tokens.ents]

    # Creates a dictionary to store all the extracted data from the post
    post_data = {
        "id": post.id,
        "title": post.title,
        "score": post.score,
        "texto": post.selftext,
        "content": content,
        "entitities": entities,
        "created_utc": created_datetime_brasilia,
        "author": author_name,
        "comments": []
    }

    # Fetches all comments from the post
    post.comments.replace_more(limit=None)

    comment_data = ""
    # Concatenates the body of all comments into a single string
    for comment in post.comments.list():
        comment_data += comment.body + "\n"

    # Processes the combined comments string using the NLP model
    doc = nlp(comment_data)
    # Extracts all words, converting to lowercase and filtering out stop words and punctuation
    words = [word.text.lower() for word in doc if (not(word.is_stop or word.is_punct) and word.is_alpha)]
    # Counts the frequency of each word
    word_freq = Counter(words)
    # Finds the 10 most common words/tokens in the comments
    commons = word_freq.most_common(10)

    # Adds the list of the 10 most common words to the post data
    post_data["comments"].append(commons)    

    # Saves to MongoDB
    try:
        collection.insert_one(post_data)
        print(f"Post saved to mongoDB: {post.title}")
    except errors.DuplicateKeyError:
        print(f"Post already exists in MongoDB: {post.title}")

# Main Function
def run_scraper():
    # Loop through each predefined search term (tickers and corporations)
    for term in terms:
        print(f"Subreddit: r/{subreddit_name} - Searching with term: {term} in the last {time_filter_reddit}")
        # Search the subreddit for posts containing the current term, using the previously defined search parameters
        posts = subreddit.search(term, sort="new", time_filter=time_filter_reddit, limit=None)
        # For each post found in the search results, call the process_and_save_post function to process it
        for post in posts:
            process_and_save_post(post)

run_scraper()

