"""db.py - database session management"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Article, Run
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()


def save_article(article: dict):
    """
    Save or update an article from a scraper.

    Expected keys in `article`:
    - source, title, summary, url, tier, weight, published, scraped_at, label, theater
    (we store the full dict in raw_metadata for later use)
    """
    with get_session() as session:
        obj = Article(
            source_key=article.get("source", "unknown"),
            url=article.get("url", ""),
            title=article.get("title", ""),
            confidence_score=article.get("weight", 0.2),
            confidence_label=article.get("label", "UNVERIFIED"),
            raw_metadata=article,
        )
        # Use merge so repeated scrapes of the same URL update the row
        session.merge(obj)
        session.commit()


def save_run(run_data: dict):
    with get_session() as session:
        obj = Run(
            article_count=run_data.get("article_count", 0),
            status=run_data.get("status", "COMPLETED"),
        )
        session.add(obj)
        session.commit()
        return obj.id


def get_recent_articles(hours: int = 24):
    """
    Return articles scraped in the last `hours` hours as dicts suitable
    for SourceEvaluator and BriefGenerator.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    with get_session() as session:
        # scraped_at lives in raw_metadata as an ISO string
        # we fetch all and filter in Python for simplicity
        rows = session.query(Article).all()

    articles = []
    for r in rows:
        meta = r.raw_metadata or {}
        scraped_at = meta.get("scraped_at")
        if scraped_at:
            try:
                dt = datetime.fromisoformat(scraped_at)
            except ValueError:
                continue
            if dt < cutoff:
                continue

        articles.append({
            "source": meta.get("source", r.source_key),
            "tier": meta.get("tier"),
            "weight": meta.get("weight"),
            "title": meta.get("title", r.title),
            "summary": meta.get("summary", ""),
            "url": meta.get("url", r.url),
            "published": meta.get("published"),
            "scraped_at": scraped_at,
            "label": meta.get("label", r.confidence_label),
            "theater": meta.get("theater"),
            "confidence_score": r.confidence_score,
            "confidence_label": r.confidence_label,
        })

    return articles
