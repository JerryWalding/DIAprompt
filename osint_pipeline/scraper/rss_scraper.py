"""
rss_scraper.py - RSS feed ingestion for Reuters, AP, BBC, ISW
Framework: v12.2
"""

import feedparser
import logging
from datetime import datetime, timezone
from config import RSS_FEEDS, SOURCE_TIERS
from database.db import save_article

logger = logging.getLogger(__name__)


class RssScraper:
    """
    Ingests RSS feeds from Tier 1-3 sources.
    Each article is stored with its source tier weight for downstream evaluation.
    """

    def __init__(self):
        self.feeds = RSS_FEEDS

    def scrape(self, sources=None):
        """
        Scrape RSS feeds. If sources is None, scrape all configured feeds.

        Args:
            sources (list|None): List of source keys to scrape, or None for all.
        """
        targets = sources if sources else list(self.feeds.keys())

        for source_key in targets:
            if source_key not in self.feeds:
                logger.warning(f"[RSS] Unknown source: {source_key}. Skipping.")
                continue

            url = self.feeds[source_key]
            logger.info(f"[RSS] Scraping {source_key}: {url}")

            try:
                feed = feedparser.parse(url)
                entries = feed.get("entries", [])
                logger.info(f"[RSS] {source_key}: {len(entries)} entries found.")

                for entry in entries:
                    article = self._parse_entry(entry, source_key)
                    save_article(article)

            except Exception as e:
                logger.error(f"[RSS] Error scraping {source_key}: {e}")

    def _parse_entry(self, entry, source_key):
        """
        Parse a feedparser entry into a normalized article dict.
        """
        tier_info = SOURCE_TIERS.get(source_key, {"tier": 5, "weight": 0.20})

        return {
            "source":      source_key,
            "tier":        tier_info["tier"],
            "weight":      tier_info["weight"],
            "title":       entry.get("title", ""),
            "summary":     entry.get("summary", ""),
            "url":         entry.get("link", ""),
            "published":   self._parse_date(entry),
            "scraped_at":  datetime.now(timezone.utc).isoformat(),
            "label":       "UNVERIFIED",
            "theater":     None,
        }

    def _parse_date(self, entry):
        """Extract published date from entry, return ISO string or None."""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
        return None
