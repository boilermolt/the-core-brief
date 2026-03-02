#!/usr/bin/env python3
"""
The Core Brief - News Aggregator
Fetches and processes nuclear industry news from multiple sources.
"""

import feedparser
import requests
from datetime import datetime, timedelta
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import hashlib
import re
from bs4 import BeautifulSoup

@dataclass
class NewsItem:
    """Represents a single news item."""
    title: str
    url: str
    source: str
    published: Optional[datetime]
    summary: str
    category: str
    keywords_matched: List[str]
    score: float = 0.0
    
    def to_dict(self):
        d = asdict(self)
        if self.published:
            d['published'] = self.published.isoformat()
        return d
    
    @property
    def id(self):
        """Generate unique ID from URL."""
        return hashlib.md5(self.url.encode()).hexdigest()


class SourceAggregator:
    """Aggregates news from multiple sources."""
    
    def __init__(self, config_path: str = "sources.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self) -> dict:
        """Load source configuration."""
        with open(self.config_path) as f:
            return yaml.safe_load(f)
    
    def fetch_rss(self, feed_url: str, source_name: str, category: str) -> List[NewsItem]:
        """Fetch items from an RSS feed."""
        items = []
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                # Parse published date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                # Extract summary
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'description'):
                    summary = entry.description
                
                item = NewsItem(
                    title=entry.title,
                    url=entry.link,
                    source=source_name,
                    published=pub_date,
                    summary=summary,
                    category=category,
                    keywords_matched=[]
                )
                items.append(item)
        except Exception as e:
            print(f"Error fetching RSS from {source_name}: {e}")
        
        return items
    
    def match_keywords(self, item: NewsItem) -> NewsItem:
        """Match keywords against item content and calculate score."""
        text = f"{item.title} {item.summary}".lower()
        matched = []
        
        for category, keywords in self.config['keywords'].items():
            for keyword in keywords:
                if keyword.lower() in text:
                    matched.append(keyword)
        
        item.keywords_matched = list(set(matched))
        item.score = len(item.keywords_matched)
        return item
    
    def fetch_reddit(self, subreddit: str, source_name: str) -> List[NewsItem]:
        """Fetch posts from a subreddit using JSON API."""
        items = []
        try:
            url = f"https://reddit.com/r/{subreddit}/hot.json?limit=25"
            headers = {'User-Agent': 'TheCoreBrief/1.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            for post in data['data']['children']:
                post_data = post['data']
                pub_date = datetime.fromtimestamp(post_data['created_utc'])
                
                item = NewsItem(
                    title=post_data['title'],
                    url=f"https://reddit.com{post_data['permalink']}",
                    source=source_name,
                    published=pub_date,
                    summary=post_data.get('selftext', '')[:500],
                    category='community',
                    keywords_matched=[]
                )
                items.append(item)
        except Exception as e:
            print(f"Error fetching Reddit r/{subreddit}: {e}")
        
        return items
    
    def fetch_nrc_events(self) -> List[NewsItem]:
        """Scrape NRC event notifications page."""
        items = []
        try:
            url = "https://www.nrc.gov/reading-rm/doc-collections/event-status/event/index.html"
            headers = {'User-Agent': 'TheCoreBrief/1.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find event table (structure may vary - this is a starting point)
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows[:20]:  # Limit to 20 most recent
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        event_num = cols[0].get_text(strip=True)
                        title = cols[1].get_text(strip=True)
                        date_str = cols[2].get_text(strip=True) if len(cols) > 2 else ""
                        
                        # Try to parse date
                        pub_date = None
                        try:
                            pub_date = datetime.strptime(date_str, '%m/%d/%Y')
                        except:
                            pass
                        
                        # Build URL (event detail page pattern)
                        event_url = f"https://www.nrc.gov/reading-rm/doc-collections/event-status/event/{event_num}.html"
                        
                        item = NewsItem(
                            title=f"NRC Event {event_num}: {title}",
                            url=event_url,
                            source="NRC Event Notifications",
                            published=pub_date,
                            summary=title,
                            category='regulatory',
                            keywords_matched=[]
                        )
                        items.append(item)
        except Exception as e:
            print(f"Error fetching NRC events: {e}")
        
        return items
    
    def fetch_all(self, days_back: int = 7) -> List[NewsItem]:
        """Fetch from all configured sources."""
        all_items = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Fetch RSS feeds
        for category in ['regulatory', 'industry_news', 'research']:
            sources = self.config.get(category, [])
            for source in sources:
                if source.get('type') == 'rss' and 'feed_url' in source:
                    print(f"Fetching {source['name']}...")
                    items = self.fetch_rss(
                        source['feed_url'],
                        source['name'],
                        category
                    )
                    all_items.extend(items)
        
        # Fetch NRC events
        print("Fetching NRC Event Notifications...")
        all_items.extend(self.fetch_nrc_events())
        
        # Fetch Reddit
        community_sources = self.config.get('community', [])
        for source in community_sources:
            if source.get('type') == 'reddit':
                subreddit = source['url'].split('/r/')[-1].strip('/')
                print(f"Fetching r/{subreddit}...")
                items = self.fetch_reddit(subreddit, f"r/{subreddit}")
                all_items.extend(items)
        
        # Filter by date and match keywords
        filtered_items = []
        for item in all_items:
            if item.published and item.published >= cutoff_date:
                item = self.match_keywords(item)
                filtered_items.append(item)
            elif not item.published:  # Include items without dates
                item = self.match_keywords(item)
                filtered_items.append(item)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_items = []
        for item in filtered_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items
    
    def rank_items(self, items: List[NewsItem]) -> List[NewsItem]:
        """Rank items by relevance score."""
        return sorted(items, key=lambda x: (x.score, x.published or datetime.min), reverse=True)
    
    def save_to_cache(self, items: List[NewsItem], filename: str = None):
        """Save items to JSON cache."""
        if filename is None:
            filename = f"fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = self.cache_dir / filename
        data = {
            'fetched_at': datetime.now().isoformat(),
            'item_count': len(items),
            'items': [item.to_dict() for item in items]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(items)} items to {output_path}")
        return output_path


def main():
    """CLI entry point."""
    aggregator = SourceAggregator()
    
    print("Fetching news from all sources...")
    items = aggregator.fetch_all(days_back=7)
    
    print(f"\nFetched {len(items)} items")
    
    print("\nRanking by relevance...")
    ranked = aggregator.rank_items(items)
    
    print("\nTop 10 stories:")
    for i, item in enumerate(ranked[:10], 1):
        print(f"\n{i}. {item.title}")
        print(f"   Source: {item.source} | Category: {item.category}")
        print(f"   Score: {item.score} | Keywords: {', '.join(item.keywords_matched[:5])}")
        print(f"   URL: {item.url}")
    
    # Save to cache
    aggregator.save_to_cache(ranked)


if __name__ == "__main__":
    main()
