from twilio.rest import Client

from app.core.config import settings


class WhatsAppSender:
    def __init__(self) -> None:
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_whatsapp_from
        self.to_number = settings.whatsapp_to

    def send_message(self, body: str) -> str:
        message = self.client.messages.create(
            from_=self.from_number,
            to=self.to_number,
            body=body
        )

        return message.sid
    