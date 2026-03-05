"""
advocacy_laundering.py - Advocacy Laundering Protocol automated filter
Framework: v12.2 Section 2.3.4

TRIGGER: Claim originates from or is amplified by a source with a direct
         stake in the outcome (government, military, advocacy org, think tank
         with known funding ties)
ACTION: Flag as INTERESTED_PARTY_UNVERIFIED; require independent corroboration
        before upgrading label
OUTCOMES: LAUNDERING_DETECTED / LAUNDERING_POSSIBLE / CLEAN

Advocacy laundering does not mean a claim is false.
It means the claim requires independent corroboration before acceptance.
Sources with institutional interests can and do report accurate information.
The protocol applies equal scrutiny regardless of which party is flagged.
"""

import logging
from config import SOURCE_TIERS, CLAIM_LABELS, PROTOCOL_THRESHOLDS

logger = logging.getLogger(__name__)

INTERESTED_PARTIES = {
    "ukrainian_general_staff": "Ukrainian MoD - direct operational stake",
    "russian_mod":             "Russian MoD - direct operational stake",
    "tass":                    "Russian state media - editorial alignment with Kremlin",
    "ria_novosti":             "Russian state media - editorial alignment with Kremlin",
    "isw_strategic":           "ISW - US-based think tank; known funding from defense contractors",
    "al_jazeera":              "Qatari state-funded - editorial alignment with Qatari foreign policy",
}


class AdvocacyLaunderingProtocol:
    """
    Implements the Advocacy Laundering Protocol from v12.2 Section 2.3.4.
    """

    def __init__(self):
        self.min_corroboration = PROTOCOL_THRESHOLDS["min_independent_corroboration"]

    def evaluate(self, claim_text: str, source_key: str, corroborating_sources: list) -> dict:
        logger.info(f"[ADVOCACY] Evaluating claim from source: {source_key}")

        is_interested = source_key in INTERESTED_PARTIES
        interest_note = INTERESTED_PARTIES.get(source_key, None)

        independent_corroboration = [
            s for s in corroborating_sources
            if s not in INTERESTED_PARTIES and s != source_key
        ]
        corroboration_count = len(independent_corroboration)

        outcome = self._determine_outcome(is_interested, corroboration_count)

        result = {
            "protocol":              "ADVOCACY_LAUNDERING_PROTOCOL",
            "source":                source_key,
            "is_interested_party":   is_interested,
            "interest_note":         interest_note,
            "corroborating_sources": corroborating_sources,
            "independent_count":     corroboration_count,
            "required_count":        self.min_corroboration,
            "outcome":               outcome["status"],
            "label":                 outcome["label"],
            "note":                  outcome["note"],
        }

        logger.info(f"[ADVOCACY] Result: {outcome['status']} | Independent corroboration: {corroboration_count}/{self.min_corroboration}")
        return result

    def _determine_outcome(self, is_interested: bool, corroboration_count: int) -> dict:
        if not is_interested:
            return {
                "status": "CLEAN",
                "label":  "UNVERIFIED",
                "note":   "Source not flagged as interested party. Standard verification applies."
            }

        if corroboration_count >= self.min_corroboration:
            return {
                "status": "LAUNDERING_POSSIBLE",
                "label":  "PROBABLE",
                "note": (
                    f"Source is an interested party but claim has {corroboration_count} independent "
                    f"corroborating sources (threshold: {self.min_corroboration}). "
                    f"Elevated to PROBABLE pending geolocated confirmation."
                )
            }

        return {
            "status": "LAUNDERING_DETECTED",
            "label":  CLAIM_LABELS["INTERESTED_PARTY_UNVERIFIED"],
            "note": (
                f"Claim originates from interested party with insufficient independent corroboration "
                f"({corroboration_count}/{self.min_corroboration} required). "
                f"Do not report as confirmed. Seek independent verification."
            )
        }

    def batch_evaluate(self, claims: list) -> list:
        return [
            self.evaluate(
                c.get("claim_text", ""),
                c.get("source_key", ""),
                c.get("corroborating_sources", [])
            )
            for c in claims
        ]
