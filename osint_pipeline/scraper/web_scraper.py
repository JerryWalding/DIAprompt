"""
web_scraper.py - Web scraping for Rybar, DeepState, ISW
Framework: v12.2
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from config import WEB_TARGETS, SOURCE_TIERS
from database.db import save_article

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OSINT-Pipeline/1.0)"
}


class WebScraper:
    """
    Scrapes web sources not available via RSS: Rybar (Telegram public),
    DeepState, ISW blog updates.
    """

    def __init__(self):
        self.targets = WEB_TARGETS

    def scrape(self, sources=None):
        targets = sources if sources else list(self.targets.keys())

        for source_key in targets:
            if source_key not in self.targets:
                logger.warning(f"[WEB] Unknown source: {source_key}. Skipping.")
                continue

            url = self.targets[source_key]
            logger.info(f"[WEB] Scraping {source_key}: {url}")

            try:
                handler = self._get_handler(source_key)
                articles = handler(url, source_key)
                for article in articles:
                    save_article(article)
                logger.info(f"[WEB] {source_key}: {len(articles)} articles saved.")

            except Exception as e:
                logger.error(f"[WEB] Error scraping {source_key}: {e}")

    def _get_handler(self, source_key):
        handlers = {
            "rybar":     self._scrape_rybar,
            "deepstate": self._scrape_deepstate,
            "isw_blog":  self._scrape_isw,
        }
        return handlers.get(source_key, self._scrape_generic)

    def _scrape_rybar(self, url, source_key):
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = []
        for post in soup.select(".tgme_widget_message_text"):
            text = post.get_text(separator=" ").strip()
            if not text:
                continue
            articles.append(self._build_article(source_key, text[:120], text, url))
        return articles

    def _scrape_deepstate(self, url, source_key):
        logger.info("[WEB] DeepState: full map scrape requires browser automation — flagging for manual review.")
        return []

    def _scrape_isw(self, url, source_key):
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = []
        for item in soup.select("article h2 a, .view-content .views-row a"):
            title = item.get_text(strip=True)
            link = item.get("href", url)
            if not link.startswith("http"):
                link = "https://www.understandingwar.org" + link
            articles.append(self._build_article("isw_tactical", title, "", link))
        return articles

    def _scrape_generic(self, url, source_key):
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else url
        return [self._build_article(source_key, title, "", url)]

    def _build_article(self, source_key, title, summary, url):
        tier_info = SOURCE_TIERS.get(source_key, {"tier": 5, "weight": 0.20})
        return {
            "source":     source_key,
            "tier":       tier_info["tier"],
            "weight":     tier_info["weight"],
            "title":      title,
            "summary":    summary,
            "url":        url,
            "published":  None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "label":      "UNVERIFIED",
            "theater":    None,
        }
