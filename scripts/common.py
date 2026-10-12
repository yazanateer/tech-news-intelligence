import logging
import sys
from pathlib import Path
from typing import Callable

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

# Conventional exit code for a process stopped with Ctrl+C (128 + SIGINT).
INTERRUPTED_EXIT_CODE = 130

logger = logging.getLogger(__name__)


def save_digest(text: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "latest_digest.txt"
    output_file.write_text(text, encoding="utf-8")
    return output_file


def run_cli(main: Callable[[], None]) -> None:
    """Run a script entry point, exiting cleanly on Ctrl+C."""
    try:
        main()
    except KeyboardInterrupt:
        # Each article is committed individually, so finished work is kept.
        logger.warning("Interrupted by user. Work completed before the interruption was saved.")
        sys.exit(INTERRUPTED_EXIT_CODE)
