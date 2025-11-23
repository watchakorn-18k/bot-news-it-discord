from newsapi import NewsApiClient
import feedparser
import dotenv
import os


dotenv.load_dotenv()


# Set up your API key and endpoint
api_key = os.getenv("API_NEWS")


# Init
newsapi = NewsApiClient(api_key=api_key)


def get_data_news():
    return newsapi.get_everything(
        q="Developer",
        language="en",
        sort_by="publishedAt",
        page_size=1,
    )


news_sources = {
    "HackerNews": "https://hnrss.org/newest",
    "Dev.to": "https://dev.to/feed",
    "TechCrunch": "https://techcrunch.com/feed/",
    "GitHub Trending": "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml"
}


def fetch_from_multiple_sources():
    all_articles = []
    for source, url in news_sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # เลือก 3 ข่าวแรกจากแต่ละแหล่ง
                all_articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": source,
                    "published": entry.get("published", "Unknown"),
                    "summary": entry.get("summary", "")
                })
        except Exception as e:
            print(f"Error fetching from {source}: {e}")
            continue
    return all_articles
