# Reddit Investment Data Scraper

## Objective
The primary objective is try to create a high-quality dataset for predictive analysis of the B3 stock market. By specifically targeting posts and comments that mention major companies and their stock tickers, this scraper aims to build a solid data foundation. This work, developed as part of my Scientific Initiation research, focuses on providing reliable, preprocessed input to enable more accurate stock market predictions, with the predictive modeling itself being beyond the scope of this study.

## Technologies and Versions
- **Python:** 3.13.1
- **PRAW:** 7.8.1
- **PyMongo:** 4.14.0
- **spaCy:** 3.8.7
- **pt_core_news_lg:** 3.8.0
- **python-dotenv:** 1.1.0
- **MongoDB:** 7.0.6
  
## How it Works
The script operates by:
1. Connecting to the Reddit API to search for posts in the `r/investimentos` subreddit.
2. Identifying posts that contain predefined financial terms (B3 tickers and company names).
3. Preprocessing the textual content of each relevant post using Natural Language Processing (NLP) with the `spaCy` library. This process extracts key linguistic features such as tokens, POS-tagging (part-of-speech), and lemmas.
4. Analyzing the comments of each post to identify the 10 most frequent tokens, which can provide valuable insights into market sentiment.
5. Storing all the structured data (post details, NLP analysis, and comment insights) into a MongoDB database.

## Setup and Installation
1. **Clone this repository:**
   `git clone https://github.com/AndreiRezende/reddit-financial-scraper`
2. **Install dependencies:**
   `pip install -r requirements.txt`
   `python -m spacy download pt_core_news_lg`
3. **Set up environment variables:**
   Create a `.env` file in the project's root directory with your credentials.
   ```
   ID_REDDIT=your_reddit_client_id
   SECRET_REDDIT=your_reddit_client_secret
   PASSWORD_REDDIT=your_reddit_password
   USER_AGENT=your_user_agent
   USERNAME_REDDIT=your_reddit_username

   MONGODB_URI=your_mongodb_connection_string
   DATABASE_MONGODB=your_database_name
   COLLECTION_MONGODB=your_collection_name 
   ```
4. **Run the scraper:**
   `python reddit_web_scraping.py`

## Observations and Future Steps
- **NER (Named Entity Recognition):** The built-in NER functionality from the SpaCy library is included in the code, but it's not currently performing as expected, often failing to accurately identify entities. While this feature is not critical to the project's main goal, it was kept in the code. Exploring alternative libraries or models may be necessary in the future, but this is considered a low-priority task for now.
- **Automatization:** For future steps, the plan is to implement Apache Airflow. Leveraging Directed Acyclic Graphs (DAGs) will not only allow the current data collection and processing to be reliably scheduled and executed, but will also provide the scalability needed to expand into more complex workflows, such as integrating data from additional sources and running future predictive analyses as part of a larger pipeline. While this task could be simply automated with tools like cron or GitHub Actions, Airflow will offer a more robust and centralized orchestration framework to handle increased complexity, monitor execution, and ensure a consistently up-to-date dataset.
