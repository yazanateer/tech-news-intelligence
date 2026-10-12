from datetime import datetime
from typing import List, Tuple

from app.models.article import Article
from app.models.article_enrichment import ArticleEnrichment


class DigestBuilder:
    def build(self, items: List[Tuple[Article, ArticleEnrichment]]) -> str:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            "עדכון חדשות טכנולוגיה",
            f"נוצר בתאריך: {now}",
            ""
        ]

        if not items:
            lines.append("לא נמצאו כתבות מועשרות.")
            return "\n".join(lines)

        for index, (article, enrichment) in enumerate(items, start=1):
            lines.append(self._format_article(article, enrichment, index))
        return "\n".join(lines)

    def build_messages(self, items: List[Tuple[Article, ArticleEnrichment]]) -> List[str]:
        if not items:
            return ["עדכון חדשות טכנולוגיה\n\nלא נמצאו כתבות מועשרות."]

        total = len(items)
        return [
            f"עדכון חדשות טכנולוגיה ({index}/{total})\n\n"
            + self._format_article(article, enrichment, index)
            for index, (article, enrichment) in enumerate(items, start=1)
        ]

    def _format_article(
        self, article: Article, enrichment: ArticleEnrichment, index: int
    ) -> str:
        tags = ", ".join(enrichment.tags) if enrichment.tags else "לא זמין"
        importance = (
            f"{enrichment.importance_score}/10"
            if enrichment.importance_score is not None
            else "לא זמין"
        )

        return "\n".join(
            [
                f"{index}. {article.title}",
                f"{enrichment.short_summary or 'לא זמין'}",
                f"למה זה חשוב: {enrichment.why_it_matters or 'לא זמין'}",
                f"תגיות: {tags}",
                f"דירוג חשיבות: {importance}",
                f"{article.canonical_url}",
                "",
            ]
        )