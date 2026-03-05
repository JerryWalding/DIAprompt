"""
silence_protocol.py - Silence Protocol automated filter
Framework: v12.2 Section 2.3.2

TRIGGER: Coverage gap >= 12 hours on active theater
ACTION: Flag for analyst review; cross-reference alternate sources
OUTCOMES: SILENCE_CONFIRMED / SILENCE_PARTIAL / NO_SILENCE

Silence does not equal absence of activity.
A coverage gap may indicate:
  - Active information suppression
  - Operational security (OPSEC) blackout
  - Technical/logistical reporting failure
  - Genuinely low activity (must be ruled out last)
"""

import logging
from datetime import datetime, timezone, timedelta
from database.db import get_recent_articles_by_theater
from config import PROTOCOL_THRESHOLDS, THEATERS

logger = logging.getLogger(__name__)


class SilenceProtocol:
    """
    Implements the Silence Protocol from v12.2 Section 2.3.2.

    Monitors active theaters for reporting gaps exceeding the configured
    silence trigger threshold. Flags gaps for analyst review with
    supporting context.
    """

    def __init__(self):
        self.threshold_hours = PROTOCOL_THRESHOLDS["silence_trigger_hours"]

    def evaluate(self, theater: str) -> dict:
        if theater not in THEATERS:
            logger.warning(f"[SILENCE] Unknown theater: {theater}")
            return {"outcome": "UNKNOWN_THEATER", "theater": theater}

        logger.info(f"[SILENCE] Evaluating silence for theater: {theater}")

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.threshold_hours)
        recent_articles = get_recent_articles_by_theater(theater, since=cutoff)

        if recent_articles:
            last_article = max(recent_articles, key=lambda a: a.get("scraped_at", ""))
            return {
                "protocol":      "SILENCE_PROTOCOL",
                "theater":       theater,
                "outcome":       "NO_SILENCE",
                "article_count": len(recent_articles),
                "last_article":  last_article.get("scraped_at"),
                "gap_hours":     0,
                "note":          f"Normal coverage: {len(recent_articles)} articles in last {self.threshold_hours}h"
            }

        all_articles = get_recent_articles_by_theater(theater, since=None)
        if all_articles:
            last_article = max(all_articles, key=lambda a: a.get("scraped_at", ""))
            last_seen = datetime.fromisoformat(last_article["scraped_at"])
            gap = datetime.now(timezone.utc) - last_seen
            gap_hours = round(gap.total_seconds() / 3600, 1)
        else:
            last_article = None
            gap_hours = None

        outcome = "SILENCE_CONFIRMED" if gap_hours and gap_hours >= self.threshold_hours else "SILENCE_PARTIAL"

        result = {
            "protocol":      "SILENCE_PROTOCOL",
            "theater":       theater,
            "outcome":       outcome,
            "gap_hours":     gap_hours,
            "last_article":  last_article.get("scraped_at") if last_article else None,
            "threshold_hrs": self.threshold_hours,
            "note":          self._generate_note(outcome, theater, gap_hours),
        }

        logger.warning(f"[SILENCE] {theater}: {outcome} — gap of {gap_hours}h detected.")
        return result

    def evaluate_all_theaters(self) -> list:
        return [self.evaluate(theater) for theater in THEATERS]

    def _generate_note(self, outcome: str, theater: str, gap_hours) -> str:
        if outcome == "SILENCE_CONFIRMED":
            return (
                f"ALERT: {theater} reporting gap of {gap_hours}h exceeds {self.threshold_hours}h threshold. "
                f"Possible causes: information suppression, OPSEC blackout, or reporting failure. "
                f"Analyst review required before assessment."
            )
        elif outcome == "SILENCE_PARTIAL":
            return (
                f"CAUTION: Reduced coverage detected for {theater}. "
                f"Gap of {gap_hours}h does not yet meet silence threshold. Monitor closely."
            )
        return f"No silence detected for {theater}."