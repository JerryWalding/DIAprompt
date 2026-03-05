"""models.py - database ORM models for OSINT pipeline"""
from sqlalchemy import Column, Integer, String, Float, Text, JSON
from sqlalchemy.orm import declarative_base
Base = declarative_base()
class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    source_key = Column(String(128), unique=True, nullable=False)
    tier = Column(Integer, default=5)
    weight = Column(Float, default=0.20)
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    source_key = Column(String(128), nullable=False)
    url = Column(String(1024), unique=True, nullable=False)
    title = Column(Text)
    confidence_score = Column(Float)
    confidence_label = Column(String(64))
    raw_metadata = Column(JSON)
class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    article_count = Column(Integer, default=0)
    status = Column(String(32), default="RUNNING")
