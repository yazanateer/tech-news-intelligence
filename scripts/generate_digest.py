import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.repositories.digest_repository import DigestRepository
from app.services.ranking.digest_builder import DigestBuilder


def main() -> None:
    db = SessionLocal()

    try:
        digest_repository = DigestRepository(db)
        digest_builder = DigestBuilder()

        items = digest_repository.get_top_enriched_articles(limit=5)
        digest = digest_builder.build(items)

        print(digest)

        output_dir = project_root / "output"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "latest_digest.txt"
        output_file.write_text(digest, encoding="utf-8")

        print(f"\nDiges saved to: {output_file}")

    finally:
        db.close()

if __name__ == "__main__":
    main()

