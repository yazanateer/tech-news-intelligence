import logging

from app.core.logging import setup_logging


def test_twilio_http_client_logs_are_silenced_below_warning() -> None:
    setup_logging()

    assert not logging.getLogger("twilio.http_client").isEnabledFor(logging.INFO)
    assert logging.getLogger("twilio.http_client").isEnabledFor(logging.WARNING)
