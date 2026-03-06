#!/usr/bin/env python3
"""
OSINT Pipeline - CLI Entry Point
Framework: v12.2 Methodological Transparency Update
UNCLASSIFIED // OPEN SOURCE INTELLIGENCE — INDEPENDENT ANALYSIS
"""

import argparse
import sys
from database.db import init_db
from scraper.rss_scraper import RssScraper
from scraper.web_scraper import WebScraper
from brief.generator import BriefGenerator
from session.state import SessionState
from analysis.source_evaluator import SourceEvaluator

def parse_args():
    parser = argparse.ArgumentParser(
        description="OSINT Pipeline - DIA-Style Intelligence Brief Generator"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Init DB
    subparsers.add_parser("init-db", help="Initialize the SQLite database")

    # Brief generation
    brief_parser = subparsers.add_parser("brief", help="Generate a brief")
    brief_parser.add_argument("--type", choices=["morning", "evening", "flash"], required=True)
    brief_parser.add_argument("--theater", default="ALL", help="Theater filter for flash briefs")

    # Scrape
    scrape_parser = subparsers.add_parser("scrape", help="Run source scraping")
    scrape_parser.add_argument("--sources", default="all", help="Comma-separated sources or 'all'" )

    # User intel
    intel_parser = subparsers.add_parser("intel", help="Log user intelligence")
    intel_parser.add_argument("--add", required=True, help="Intelligence text")
    intel_parser.add_argument("--source", default="user")
    intel_parser.add_argument("--id", type=int, help="Contribution ID number")

    # Projections
    proj_parser = subparsers.add_parser("projections", help="Query projection database")
    proj_parser.add_argument("--status", choices=["pending", "confirmed", "incorrect", "all"], default="pending")
    proj_parser.add_argument("--since", help="Filter by date (YYYY-MM-DD)")

    # Session
    session_parser = subparsers.add_parser("session", help="Manage session state")
    session_parser.add_argument("--show", action="store_true")
    session_parser.add_argument("--reset", action="store_true")

    return parser.parse_args()

def main():
    args = parse_args()

    if args.command == "init-db" or args.command is None:
        print("[INIT] Initializing OSINT Pipeline database...")
        init_db()
        print("[INIT] Database initialized successfully.")
        return

    if args.command == "brief":
        gen = BriefGenerator()
        evaluator = SourceEvaluator()

        # 1. Get recent articles from DB (last 24 hours)
        articles = get_recent_articles(hours=24)

        if not articles:
            print("[BRIEF] No recent articles found. Run 'scrape' first.")
            return

        # 2. Evaluate credibility
        articles = evaluator.evaluate_batch(articles)

        # 3. Aggregate by location/status
        aggregated = []
        by_location = {}

        for a in articles:
            text = (a.get("title", "") + " " + a.get("summary", "")).lower()

            if "ukraine" in text:
                loc = "UKRAINE"
            elif any(k in text for k in ["gaza", "israel", "iran"]):
                loc = "MIDDLE_EAST"
            else:
                loc = "OPPORTUNISTIC"

            score = a.get("credibility_score", a.get("weight", 0.2))

            if loc not in by_location:
                by_location[loc] = {
                    "location": loc,
                    "status": "NOMINAL",
                    "total_score": 0.0,
                    "article_count": 0,
                }

            by_location[loc]["total_score"] += score
            by_location[loc]["article_count"] += 1

        for loc, data in by_location.items():
            if data["total_score"] > 5:
                data["status"] = "ALERT"
            elif data["total_score"] > 2:
                data["status"] = "WATCH"
            aggregated.append(data)

        # 4. Generate and print the brief
        brief_obj = gen.generate(aggregated, articles, run_id=None)
        brief_text = gen.to_text(brief_obj)
        print(brief_text)

    elif args.command == "scrape":
        sources = args.sources.split(",") if args.sources != "all" else None
        rss = RssScraper()
        web = WebScraper()
        rss.scrape(sources=sources)
        web.scrape(sources=sources)
        print("[SCRAPE] Source scraping complete.")

    elif args.command == "intel":
        state = SessionState()
        state.log_user_intel(
            text=args.add,
            source=args.source,
            contribution_id=args.id
        )
        print(f"[INTEL] Logged user intelligence contribution #{args.id}.")

    elif args.command == "projections":
        from database.db import query_projections
        results = query_projections(status=args.status, since=args.since)
        for r in results:
            print(r)

    elif args.command == "session":
        state = SessionState()
        if args.show:
            state.display()
        elif args.reset:
            state.reset()
            print("[SESSION] Session state reset.")

if __name__ == "__main__":
    main()
