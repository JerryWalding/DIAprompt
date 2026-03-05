"""confidence_scorer.py - Composite Confidence Scoring Engine. Framework: v12.2 Section 3.3"""
from config import CLAIM_LABELS, CONFIDENCE_THRESHOLDS

class ConfidenceScorer:
    def score(self, a: dict) -> dict:
        c = a.get("credibility_score", 0.0)
        i = a.get("indicator_score", 0.0)
        p = 0.20 if a.get("advocacy_outcome") == "LAUNDERING_DETECTED" else 0.0
        final = round(max(0.0, min(1.0, (c * 0.5) + (i * 0.3) - (p * 0.2))), 4)
        a["confidence_score"] = final
        a["confidence_label"] = self._label(final)
        return a

    def score_batch(self, articles: list) -> list:
        return [self.score(a) for a in articles]

    def _label(self, s: float) -> str:
        t = CONFIDENCE_THRESHOLDS
        if s >= t.get("confirmed", 0.85):   return CLAIM_LABELS.get("CONFIRMED", "CONFIRMED")
        if s >= t.get("probable", 0.65):    return CLAIM_LABELS.get("PROBABLE", "PROBABLE")
        if s >= t.get("possible", 0.40):    return CLAIM_LABELS.get("POSSIBLE", "POSSIBLE")
        if s >= t.get("speculative", 0.20): return CLAIM_LABELS.get("SPECULATIVE", "SPECULATIVE")
        return CLAIM_LABELS.get("UNVERIFIED", "UNVERIFIED")
