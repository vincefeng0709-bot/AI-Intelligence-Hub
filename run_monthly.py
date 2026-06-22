#!/usr/bin/env python3
"""Monthly runner: generate monthly trends report → build site."""
import sys
import logging
import argparse
from datetime import date

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("run_monthly")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str)
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else None

    from config.settings import ANTHROPIC_API_KEY
    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set")
        sys.exit(1)

    logger.info("Generating monthly report...")
    from src.generators.monthly_generator import generate_monthly_report
    report = generate_monthly_report(target_date)
    logger.info(f"Monthly report generated ({len(report)} chars)")

    logger.info("Building static site...")
    from src.publishers.site_generator import build_site
    build_site()
    logger.info("Done!")


if __name__ == "__main__":
    main()
