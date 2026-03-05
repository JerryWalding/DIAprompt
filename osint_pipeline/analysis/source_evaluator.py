"""source_evaluator.py - Source credibility evaluation engine. Framework: v12.2"""
import logging
from config import SOURCE_TIERS
from protocols.advocacy_laundering import INTERESTED_PARTIES

logger = logging.getLogger(__name__)

class SourceEvaluator:
    def evaluate(self, article: dict) -> dict:
        src = article.get("source", "unknown")
        info = SOURCE_TIERS.get(src, {"tier": 5, "weight": 0.20})
        score = round(max(0.0, min(1.0, info["weight"] - (0.10 if src in INTERESTED_PARTIES else 0.0))), 3)
        article["credibility_score"] = score
        article["credibility_note"] = f"tier={{info['tier']}} final={{score}}"
        return article
    def evaluate_batch(self, articles: list) -> list:
        return [self.evaluate(a) for a in articles]
    def get_tier(self, src: str) -> int:
        return SOURCE_TIERS.get(src, {"tier": 5})["tier"]
    def is_tier1(self, src: str) -> bool:
        return self.get_tier(src) == 1