from newsapi import NewsApiClient
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Set up your API key and endpoint
api_key = getenv("API_NEWS")

# Init
newsapi = NewsApiClient(api_key=api_key)

def get_data():
    return newsapi.get_everything(
        q="Programming",
        language="en",
        sort_by="publishedAt",
        page_size=1,
    )
