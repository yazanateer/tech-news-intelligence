from datetime import datetime
from typing import List, Tuple

from app.models.article import Article
from app.models.article_enrichment import ArticleEnrichment


class DigestBuilder:
    def build(self, items: List[Tuple[Article, ArticleEnrichment]]) -> str:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            "Israeli Tech News Digest",
            f"Generated at: {now}",
            ""
        ]

        if not items:
            lines.append("No enriched articles found.")
            return "\n".join(lines)

        for index, (article, enrichment) in enumerate(items, start=1):
            tags = ", ".join(enrichment.tags) if enrichment.tags else "N/A"
            importance = (
                enrichment.importance_score
                if enrichment.importance_score is not None
                else "N/A"
            )

            lines.extend(
                [
                    f"{index}. {article.title}",
                    f"Summary: {enrichment.short_summary or 'N/A'}",
                    f"Why it matters: {enrichment.why_it_matters or 'N/A'}",
                    f"Tags: {tags}",
                    f"Importance: {importance}",
                    f"URL: {article.canonical_url}",
                    "",
                ]
            )
        return "\n".join(lines)