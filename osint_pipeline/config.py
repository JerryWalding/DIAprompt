"""
config.py - Source URLs, tier weights, protocol thresholds
Framework: v12.2
UNCLASSIFIED // OPEN SOURCE INTELLIGENCE — INDEPENDENT ANALYSIS
"""

# ─── SOURCE TIER WEIGHTS (v12.2 Section 2.1) ───────────────────────────────

SOURCE_TIERS = {
    # Tier 1: 85-100%
    "geolocated_video":       {"tier": 1, "weight": 0.95},
    "reuters_wire":           {"tier": 1, "weight": 0.90},
    "ap_wire":                {"tier": 1, "weight": 0.90},
    "official_press_release": {"tier": 1, "weight": 0.87},

    # Tier 2: 75-90%
    "deepstate_map":          {"tier": 2, "weight": 0.85},
    "bbc":                    {"tier": 2, "weight": 0.82},
    "nyt":                    {"tier": 2, "weight": 0.80},
    "cnn":                    {"tier": 2, "weight": 0.78},
    "rybar":                  {"tier": 2, "weight": 0.83},
    "military_summary":       {"tier": 2, "weight": 0.80},

    # Tier 3: 40-65%
    "isw_tactical":           {"tier": 3, "weight": 0.58},
    "isw_strategic":          {"tier": 3, "weight": 0.40},
    "ukrainian_general_staff":{"tier": 3, "weight": 0.50},
    "russian_mod":            {"tier": 3, "weight": 0.52},

    # Tier 4: 30-50%
    "tass":                   {"tier": 4, "weight": 0.40},
    "ria_novosti":            {"tier": 4, "weight": 0.38},
    "al_jazeera":             {"tier": 4, "weight": 0.45},

    # Tier 5: <30%
    "unverified_social":      {"tier": 5, "weight": 0.20},

    # User intelligence: received as UNVERIFIED, upgraded on confirmation
    "user_intel":             {"tier": None, "weight": None},
}

# ─── RSS FEED URLS ──────────────────────────────────────────────────────────

RSS_FEEDS = {
    "reuters": "https://feeds.reuters.com/reuters/worldNews",
    "ap":      "https://rsshub.app/apnews/topics/world-news",
    "bbc":     "http://feeds.bbci.co.uk/news/world/rss.xml",
    "isw":     "https://www.understandingwar.org/rss.xml",
}

# ─── WEB SCRAPE TARGETS ─────────────────────────────────────────────────────

WEB_TARGETS = {
    "rybar":     "https://t.me/s/rybar",
    "deepstate": "https://deepstatemap.live",
    "isw_blog":  "https://www.understandingwar.org/backgrounder/ukraine-conflict-updates",
}

# ─── THEATERS ───────────────────────────────────────────────────────────────

THEATERS = [
    "MIDDLE_EAST",
    "UKRAINE",
    "CARIBBEAN",
    "OPPORTUNISTIC",
]

# ─── PROTOCOL THRESHOLDS ────────────────────────────────────────────────────

PROTOCOL_THRESHOLDS = {
    "silence_trigger_hours": 12,
    "distraction_coverage_gap_ratio": 0.4,
    "min_independent_corroboration": 2,
}

# ─── CLAIM LABELS ───────────────────────────────────────────────────────────

CLAIM_LABELS = {
    "CONFIRMED":                   "Two or more independent credible sources",
    "PROBABLE":                    "Single credible source + corroborating circumstantial evidence",
    "UNVERIFIED":                  "Single source; not yet cross-referenced",
    "SPECULATIVE":                 "Analytical inference; no direct sourcing",
    "CONTRADICTED":                "Claim conflicts with available evidence",
    "INTERESTED_PARTY_UNVERIFIED": "Claim from source with direct stake; requires independent corroboration",
}

# ─── DATABASE PATH ───────────────────────────────────────────────────────────

DB_PATH = "osint_pipeline.db"

# ─── BRIEF SCHEDULE (EST) ────────────────────────────────────────────────────

BRIEF_SCHEDULE = {
    "morning": {"start": "08:00", "end": "09:00"},
    "evening": {"start": "18:00", "end": "21:00"},
    "flash":   {"start": None,    "end": None},
}