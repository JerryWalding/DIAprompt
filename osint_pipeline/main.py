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

    # TODO: replace this with real aggregated + articles when the pipeline is wired
        aggregated = [
            {"location": "UKRAINE", "status": "ALERT", "total_score": 0.9},
            {"location": "MIDDLE_EAST", "status": "WATCH", "total_score": 0.7},
        ]
        articles = [
            {
                "source": "reuters",
                "title": "Heavy fighting reported in eastern Ukraine",
                "summary": "Clashes intensified near key frontline towns.",
                "url": "https://example.com/ukraine1",
                "confidence_label": "PROBABLE",
            },
            {
                "source": "bbc",
                "title": "Tensions rise in Middle East region",
                "summary": "Regional actors mobilize forces along border.",
                "url": "https://example.com/me1",
                "confidence_label": "UNVERIFIED",
            },
        ]
        
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
