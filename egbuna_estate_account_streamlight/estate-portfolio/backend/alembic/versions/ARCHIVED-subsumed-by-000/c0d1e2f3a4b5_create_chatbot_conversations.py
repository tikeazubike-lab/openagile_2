"""Create chatbot_conversations table for F-022

Revision ID: c0d1e2f3a4b5
Revises: b0c1d2e3f4a5
Create Date: 2026-07-16 20:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = 'c0d1e2f3a4b5'
down_revision: Union[str, None] = 'b0c1d2e3f4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chatbot_conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(),
                  sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('matched_intent', sa.String(100), nullable=True),
        sa.Column('extracted_entities', JSONB, nullable=True),
        sa.Column('execution_status', sa.String(20),
                  nullable=False, server_default='matched'),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('chatbot_conversations')
