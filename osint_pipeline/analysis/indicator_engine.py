"""indicator_engine.py - Tactical Indicator Detection Engine. Framework: v12.2 Section 3.2"""
import logging
from config import INDICATOR_WEIGHTS, INDICATOR_THRESHOLDS
logger = logging.getLogger(__name__)
KEYWORDS = {"GREY_ZONE": ["grey zone", "gray zone", "contested"], "EVACUATION": ["evacuation", "humanitarian corridor"], "WITHDRAWAL": ["withdrawal", "tactical retreat", "repositioning"], "LOGISTICS": ["supply line cut", "ammunition shortage"], "C2": ["command post destroyed", "C2 degraded"], "AIR": ["drone swarm", "electronic warfare", "air defense degraded"]}
class IndicatorEngine:
    def scan_article(self, a):
        text = (a.get("title","") + " " + a.get("summary","") + " " + a.get("body","")).lower()
        det = []
        score = 0.0
        for k, kws in KEYWORDS.items():
            if any(w in text for w in kws):
                wt = INDICATOR_WEIGHTS.get(k, 0.1)
                adj = round(wt * a.get("credibility_score", 0.5), 4)
                det.append({"indicator": k, "weight": wt, "adjusted": adj})
                score += adj
        a["indicators_detected"] = det
        a["indicator_score"] = round(score, 4)
        return a
    def scan_batch(self, articles):
        return [self.scan_article(a) for a in articles]
    def aggregate_scores(self, articles, location):
        rel = [a for a in articles if location.lower() in (a.get("title","") + a.get("summary","")).lower()]
        if not rel:
            return {"location": location, "status": "NO_DATA", "total_score": 0.0, "alert": False}
        total = sum(a.get("indicator_score", 0.0) for a in rel)
        at = INDICATOR_THRESHOLDS.get("alert", 0.75)
        wt = INDICATOR_THRESHOLDS.get("watch", 0.40)
        status = "ALERT" if total >= at else "WATCH" if total >= wt else "NOMINAL"
        return {"location": location, "status": status, "total_score": round(total, 4), "alert": status == "ALERT"}