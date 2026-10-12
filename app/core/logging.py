import logging
import sys

# Third-party loggers that are too verbose at INFO. Twilio's HTTP client logs
# full request/response details, including the account SID in the URL.
NOISY_LOGGERS = ("twilio.http_client",)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
