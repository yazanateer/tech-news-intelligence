import logging
from typing import Optional

from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from app.core.config import settings

logger = logging.getLogger(__name__)


class DeliveryError(Exception):
    """Raised when a WhatsApp message could not be delivered to Twilio."""


class WhatsAppSender:
    def __init__(self, client: Optional[Client] = None) -> None:
        self.client = client or Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_whatsapp_from
        self.to_number = settings.whatsapp_to

    def send_message(self, body: str) -> str:
        try:
            message = self.client.messages.create(
                from_=self.from_number,
                to=self.to_number,
                body=body
            )
        except TwilioException as exc:
            logger.error("Twilio delivery failed: %s", exc)
            raise DeliveryError(f"Twilio delivery failed: {exc}") from exc

        logger.info("WhatsApp message sent. Twilio SID: %s", message.sid)
        return message.sid
