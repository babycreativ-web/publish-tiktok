import requests
import xml.etree.ElementTree as ET
import html
import os

def fetch_top_news(category="general"):
    """
    Fetches the latest news from Google News RSS based on category.
    Categories supported by the pipeline: politics, sports, tech, general.
    """
    print(f"📡 Fetching top news for category: {category}...")
    
    # Map friendly names to search queries (US-focused + Viral/Trending)
    query_map = {
        "politics": "trending politics news USA breaking",
        "sports": "viral sports highlights trending USA",
        "tech": "latest AI technology breakthrough trending",
        "general": "viral trending news USA breaking"
    }
    
    query = query_map.get(category.lower(), category)
    
    # Try 12h first, fallback to 1d if needed
    for timeframe in ["12h", "1d"]:
        query_with_time = f"{query} when:{timeframe}"
        encoded_query = requests.utils.quote(query_with_time)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            if items:
                top_story = items[0]
                title = top_story.find('title').text
                link = top_story.find('link').text
                pub_date = top_story.find('pubDate').text
                clean_title = title.split(" - ")[0] if " - " in title else title
                
                print(f"✅ Found Story ({timeframe}): {clean_title}")
                return {
                    "headline": clean_title,
                    "source_link": link,
                    "date": pub_date,
                    "category": category,
                    "freshness": timeframe
                }
        except Exception as e:
            print(f"⚠️ Attempt with {timeframe} failed: {e}")
            
    return None

if __name__ == "__main__":
    # Test
    news = fetch_top_news("tech")
    if news:
        print(news)
