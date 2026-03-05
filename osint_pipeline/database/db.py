"""db.py - database session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config import DATABASE_URL
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
def init_db():
    Base.metadata.create_all(bind=engine)
def get_session():
    return SessionLocal()
def save_article(session, article):
    from database.models import Article
    session.merge(Article(source_key=article.get("source","unknown"), url=article.get("url",""), title=article.get("title"), confidence_score=article.get("confidence_score"), confidence_label=article.get("confidence_label"), raw_metadata=article))
    session.commit()
def save_run(session, run_data):
    from database.models import Run
    obj = Run(article_count=run_data.get("article_count",0), status=run_data.get("status","COMPLETED"))
    session.add(obj)
    session.commit()
    return obj.id