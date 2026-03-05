"""
denial_protocol.py - Denial Protocol automated filter
Framework: v12.2 Section 2.3.1

TRIGGER: Ukrainian official denies Russian territorial claim
ACTION: Cross-reference geolocated video, DeepState, Rybar, ISW
OUTCOMES: CONFIRMED_UA / CONFIRMED_RU / GREY_ZONE / UNVERIFIED

NOT an automatic acceptance of Russian claims.
NOT an automatic dismissal of Ukrainian claims.
Requires independent verification before any conclusion.
"""

import logging
from database.db import get_articles_by_keyword

logger = logging.getLogger(__name__)


class DenialProtocol:
    """
    Implements the Denial Protocol from v12.2 Section 2.3.1.

    Empirical basis: documented pattern across Soledar, Bakhmut, Avdiivka,
    Rizdvyanka — official Ukrainian denial subsequently contradicted by
    geolocated video evidence. Pattern informs scrutiny level; does NOT
    determine outcome.
    """

    DENIAL_KEYWORDS = [
        "we hold", "under our control", "repelled", "no Russian forces",
        "did not capture", "false claim", "enemy did not",
        "ukrainian forces remain", "situation is under control",
    ]

    GREY_ZONE_KEYWORDS = [
        "grey zone", "gray zone", "contested", "difficult situation",
        "heavy fighting", "stabilizing"
    ]

    def evaluate(self, claim_text: str, location: str) -> dict:
        logger.info(f"[DENIAL] Evaluating denial for location: {location}")

        grey_zone_detected = any(
            kw.lower() in claim_text.lower() for kw in self.GREY_ZONE_KEYWORDS
        )
        if grey_zone_detected:
            logger.warning(f"[DENIAL] GREY ZONE language detected for {location} — collapse 1-10 days (Indicator #1)")

        geo_evidence = get_articles_by_keyword(location, source_filter=["geolocated_video"])
        deepstate_evidence = get_articles_by_keyword(location, source_filter=["deepstate_map"])
        rybar_evidence = get_articles_by_keyword(location, source_filter=["rybar"])
        isw_evidence = get_articles_by_keyword(location, source_filter=["isw_tactical"])

        outcome = self._determine_outcome(geo_evidence, deepstate_evidence, rybar_evidence, isw_evidence)

        result = {
            "protocol":       "DENIAL_PROTOCOL",
            "location":       location,
            "claim":          claim_text[:200],
            "grey_zone":      grey_zone_detected,
            "outcome":        outcome["status"],
            "confidence":     outcome["confidence"],
            "evidence_count": len(geo_evidence) + len(deepstate_evidence) + len(rybar_evidence),
            "label":          outcome["label"],
            "note":           outcome["note"],
        }

        logger.info(f"[DENIAL] Result for {location}: {result['outcome']} ({result['confidence']})")
        return result

    def _determine_outcome(self, geo, deepstate, rybar, isw):
        if geo:
            ru_geo = [a for a in geo if self._indicates_russian_control(a)]
            ua_geo = [a for a in geo if self._indicates_ukrainian_control(a)]
            if ru_geo and not ua_geo:
                return {"status": "CONFIRMED_RU", "confidence": "HIGH", "label": "CONFIRMED", "note": "Geolocated video evidence confirms Russian control"}
            if ua_geo and not ru_geo:
                return {"status": "CONFIRMED_UA", "confidence": "HIGH", "label": "CONFIRMED", "note": "Geolocated video evidence confirms Ukrainian control"}

        if rybar and deepstate:
            return {"status": "GREY_ZONE", "confidence": "MEDIUM", "label": "PROBABLE", "note": "Rybar and DeepState evidence present; geolocated video required for confirmation"}

        return {"status": "UNVERIFIED", "confidence": "LOW", "label": "UNVERIFIED", "note": "Insufficient independent evidence; investigation ongoing"}

    def _indicates_russian_control(self, article: dict) -> bool:
        text = (article.get("title", "") + " " + article.get("summary", "")).lower()
        return any(kw in text for kw in ["russian forces", "russian troops", "captured by russia", "under russian"])

    def _indicates_ukrainian_control(self, article: dict) -> bool:
        text = (article.get("title", "") + " " + article.get("summary", "")).lower()
        return any(kw in text for kw in ["ukrainian forces", "ukrainian troops", "held by ukraine", "under ukrainian"])
