from newsapi import NewsApiClient
import dotenv
import os
import datetime


dotenv.load_dotenv()


# Set up your API key and endpoint
api_key = os.getenv("API_NEWS")


# Init
newsapi = NewsApiClient(api_key=api_key)


def get_data():
    return newsapi.get_everything(
        q="technology and programing",
        language="en",
        sort_by="publishedAt",
        page_size=1,
    )
