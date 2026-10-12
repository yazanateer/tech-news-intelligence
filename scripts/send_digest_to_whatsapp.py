import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.repositories.digest_repository import DigestRepository
from app.services.delivery.whatsapp_sender import WhatsAppSender
from app.services.ranking.digest_builder import DigestBuilder


def main() -> None:
    db = SessionLocal()
    try:
        digest_repository = DigestRepository(db)
        digest_builder = DigestBuilder()
        whatsapp_sender = WhatsAppSender()

        items = digest_repository.get_top_enriched_articles(limit=5)
        messages = digest_builder.build_messages(items)

        for message in messages:
            message_sid = whatsapp_sender.send_message(message)
            print(f"Sent WhatsApp message. Twilio message SID: {message_sid}")

        print(f"Digest sent to WhatsApp successfully ({len(messages)} message(s)).")

    finally:
        db.close()


if __name__ == "__main__":
    main()