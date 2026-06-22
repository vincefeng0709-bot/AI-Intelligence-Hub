#!/usr/bin/env python3
"""
Daily runner: collect data → generate daily report + research digest →
run Claude tracker → build static site.

Usage:
    python run_daily.py              # run everything for today
    python run_daily.py --date 2025-06-22  # specific date
    python run_daily.py --skip-site  # skip site build
"""
import sys
import logging
import argparse
from datetime import date

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("run_daily")


def main():
    parser = argparse.ArgumentParser(description="XinyMao AI Intelligence Hub - Daily Runner")
    parser.add_argument("--date", type=str, help="Target date YYYY-MM-DD (default: today Beijing)")
    parser.add_argument("--skip-site", action="store_true", help="Skip static site build")
    parser.add_argument("--only", choices=["daily", "research", "tracker", "site"],
                        help="Run only one component")
    args = parser.parse_args()

    target_date = None
    if args.date:
        target_date = date.fromisoformat(args.date)

    from config.settings import ANTHROPIC_API_KEY
    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY is not set. Export it and retry.")
        sys.exit(1)

    only = args.only

    if only in (None, "daily"):
        logger.info("=" * 60)
        logger.info("Step 1: Generating Daily Report")
        logger.info("=" * 60)
        try:
            from src.generators.daily_generator import generate_daily_report
            report = generate_daily_report(target_date)
            logger.info(f"Daily report generated ({len(report)} chars)")
        except Exception as e:
            logger.error(f"Daily report failed: {e}", exc_info=True)

    if only in (None, "research"):
        logger.info("=" * 60)
        logger.info("Step 2: Generating Research Digest")
        logger.info("=" * 60)
        try:
            from src.generators.research_generator import generate_research_digest
            digest = generate_research_digest(target_date)
            logger.info(f"Research digest generated ({len(digest)} chars)")
        except Exception as e:
            logger.error(f"Research digest failed: {e}", exc_info=True)

    if only in (None, "tracker"):
        logger.info("=" * 60)
        logger.info("Step 3: Running Trackers")
        logger.info("=" * 60)
        try:
            from src.trackers.claude_tracker import run_claude_tracker
            run_claude_tracker()
            logger.info("Claude tracker updated")
        except Exception as e:
            logger.error(f"Claude tracker failed: {e}", exc_info=True)

        try:
            from src.trackers.openai_tracker import run_openai_tracker
            run_openai_tracker()
            logger.info("OpenAI tracker updated")
        except Exception as e:
            logger.error(f"OpenAI tracker failed: {e}", exc_info=True)

        try:
            from src.trackers.google_tracker import run_google_tracker
            run_google_tracker()
            logger.info("Google tracker updated")
        except Exception as e:
            logger.error(f"Google tracker failed: {e}", exc_info=True)

    if only in (None, "site") and not args.skip_site:
        logger.info("=" * 60)
        logger.info("Step 4: Building Static Site")
        logger.info("=" * 60)
        try:
            from src.publishers.site_generator import build_site
            build_site()
            logger.info("Static site built successfully")
        except Exception as e:
            logger.error(f"Site build failed: {e}", exc_info=True)

    logger.info("=" * 60)
    logger.info("Done!")


if __name__ == "__main__":
    main()
