"""unique enrichment per article

Revision ID: b6bb61937acc
Revises: 8231d15c168e
Create Date: 2026-10-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b6bb61937acc'
down_revision: Union[str, Sequence[str], None] = '8231d15c168e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keep only the oldest enrichment per article before enforcing uniqueness.
    op.execute(
        """
        DELETE FROM article_enrichments duplicate
        USING article_enrichments original
        WHERE duplicate.article_id = original.article_id
          AND duplicate.id > original.id
        """
    )
    op.drop_index(op.f('ix_article_enrichments_article_id'), table_name='article_enrichments')
    op.create_index(op.f('ix_article_enrichments_article_id'), 'article_enrichments', ['article_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_article_enrichments_article_id'), table_name='article_enrichments')
    op.create_index(op.f('ix_article_enrichments_article_id'), 'article_enrichments', ['article_id'], unique=False)
