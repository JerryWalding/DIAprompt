"""generator.py - Intelligence Brief Generator. Framework: v12.2 Section 5.1"""
from datetime import datetime, timezone
SECTION_ORDER = ["ALERT", "WATCH", "NOMINAL"]
class BriefGenerator:
    def generate(self, aggregated, articles, run_id=None):
        ts = datetime.now(timezone.utc).isoformat()
        sections = []
        for agg in sorted(aggregated, key=lambda x: SECTION_ORDER.index(x.get("status","NOMINAL"))):
            loc = agg.get("location","UNKNOWN")
            st = agg.get("status","NOMINAL")
            rel = [a for a in articles if loc.lower() in (a.get("title","")+a.get("summary","")).lower()]
            sections.append({"location":loc,"status":st,"total_score":agg.get("total_score",0.0),"alert":st=="ALERT","article_count":len(rel),"entries":[{"source":a.get("source",""),'title':a.get("title",""),"url":a.get("url",""),"confidence":a.get("confidence_label","UNVERIFIED")} for a in rel]})
        return {"run_id":run_id,"generated_at":ts,"section_count":len(sections),"alert_count":sum(1 for s in sections if s["alert"]),"sections":sections}
    def to_text(self, brief):
        lines=["="*72,f"INTELLIGENCE BRIEF | {brief['generated_at']}" ,"="*72]
        for s in brief.get("sections",[]):
            lines.append(f"\n[{s['status']}] {s['location'].upper()}")
            for e in s.get("entries",[]):
                lines.append(f"  - [{e['confidence']}] {e['title']} ({e['source']})")
        lines.append("="*72)
        return "\n".join(lines)