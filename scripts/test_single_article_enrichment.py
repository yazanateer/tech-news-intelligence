import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.article import Article
from app.services.ai.enrichment_service import EnrichmentService


def main() -> None:
    db = SessionLocal()

    try:
        article = db.query(Article).order_by(Article.id.desc()).first()

        if not article:
            print("No articles found in database.")
            return

        service = EnrichmentService(db)
        result = service.enrich_article(article)

        print("Enrichment completed successfully.")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()