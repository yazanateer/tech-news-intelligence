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
        digest = digest_builder.build(items)

        message_sid = whatsapp_sender.send_message(digest)

        print("Digest sent to WhatsApp successfully.")
        print(f"Twilio message SID: {message_sid}")

    finally:
        db.close()


if __name__ == "__main__":
    main()