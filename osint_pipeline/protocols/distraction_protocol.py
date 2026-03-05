"""
distraction_protocol.py - Distraction Protocol automated filter
Framework: v12.2 Section 2.3.3

TRIGGER: High-volume coverage of secondary theater while primary theater
         goes silent or underreported
ACTION: Flag coverage imbalance; cross-reference primary theater sources
OUTCOMES: DISTRACTION_CONFIRMED / DISTRACTION_POSSIBLE / NO_DISTRACTION

A distraction event does not imply intentional manipulation.
Coverage imbalance may indicate:
  - Genuine breaking news drawing legitimate attention
  - Coordinated information operation
  - Organic editorial prioritization
  - Bandwidth limitations in reporting infrastructure
Analyst judgment required before any conclusion.
"""

import logging
from database.db import get_recent_articles_by_theater
from datetime import datetime, timezone, timedelta
from config import PROTOCOL_THRESHOLDS, THEATERS

logger = logging.getLogger(__name__)


class DistractionProtocol:
    """
    Implements the Distraction Protocol from v12.2 Section 2.3.3.

    Detects coverage imbalances between theaters that may indicate
    a distraction operation or organic editorial prioritization.
    """

    def __init__(self):
        self.gap_ratio = PROTOCOL_THRESHOLDS["distraction_coverage_gap_ratio"]
        self.window_hours = 12

    def evaluate(self, primary_theater: str, secondary_theater: str) -> dict:
        logger.info(f"[DISTRACTION] Evaluating: primary={{primary_theater}}, secondary={{secondary_theater}}")

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.window_hours)
        primary_articles   = get_recent_articles_by_theater(primary_theater, since=cutoff)
        secondary_articles = get_recent_articles_by_theater(secondary_theater, since=cutoff)

        primary_count   = len(primary_articles)
        secondary_count = len(secondary_articles)

        if secondary_count == 0:
            ratio = 0.0
        else:
            ratio = primary_count / secondary_count

        outcome = self._determine_outcome(ratio, primary_count, secondary_count)

        result = {
            "protocol":          "DISTRACTION_PROTOCOL",
            "primary_theater":   primary_theater,
            "secondary_theater": secondary_theater,
            "primary_count":     primary_count,
            "secondary_count":   secondary_count,
            "coverage_ratio":    round(ratio, 3),
            "outcome":           outcome["status"],
            "label":             outcome["label"],
            "note":              outcome["note"],
        }

        logger.info(f"[DISTRACTION] Result: {{outcome['status']}} (ratio={{ratio:.3f}})")
        return result

    def evaluate_all(self) -> list:
        results = []
        for primary in THEATERS:
            for secondary in THEATERS:
                if primary != secondary:
                    results.append(self.evaluate(primary, secondary))
        return results

    def _determine_outcome(self, ratio: float, primary_count: int, secondary_count: int) -> dict:
        if primary_count == 0 and secondary_count > 5:
            return {
                "status": "DISTRACTION_CONFIRMED",
                "label":  "PROBABLE",
                "note": (
                    f"Primary theater has zero coverage while secondary has {{secondary_count}} articles. "
                    f"Significant coverage imbalance detected. Analyst review required."
                )
            }

        if ratio <= self.gap_ratio and secondary_count > 3:
            return {
                "status": "DISTRACTION_POSSIBLE",
                "label":  "SPECULATIVE",
                "note": (
                    f"Coverage ratio {{ratio:.2f}} is below threshold {{self.gap_ratio}}. "
                    f"Primary underreported relative to secondary. Monitor for escalation."
                )
            }

        return {
            "status": "NO_DISTRACTION",
            "label":  "UNVERIFIED",
            "note":   f"Coverage ratio {{ratio:.2f}} within normal parameters. No distraction pattern detected."
        }