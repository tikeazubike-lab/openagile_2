"""Phase 2B updates

Revision ID: 3f4739d78390
Revises: 001
Create Date: 2026-04-25 19:49:51.457938+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3f4739d78390'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── holdings ──
    op.add_column('holdings', sa.Column('holding_type', sa.String(length=20), server_default='active', nullable=False))
    op.add_column('holdings', sa.Column('cost_basis_override', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('holdings', sa.Column('obsidian_imported', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('holdings', sa.Column('obsidian_last_synced', sa.DateTime(timezone=True), nullable=True))

    # ── companies ──
    op.drop_constraint('chk_status', 'companies', type_='check')
    op.create_check_constraint('companies_status_check', 'companies', "status IN ('listed','delisted','defunct','merged','uncertain','active','inactive')")
    
    op.add_column('companies', sa.Column('obsidian_slug', sa.String(length=255), nullable=True))
    op.create_unique_constraint('uq_companies_obsidian_slug', 'companies', ['obsidian_slug'])
    op.add_column('companies', sa.Column('obsidian_imported', sa.Boolean(), server_default='false', nullable=False))

    # ── dividends ──
    op.add_column('dividends', sa.Column('dividend_type', sa.String(length=50), server_default='final', nullable=False))
    op.add_column('dividends', sa.Column('payment_status', sa.String(length=30), server_default='paid', nullable=False))
    op.add_column('dividends', sa.Column('source', sa.String(length=50), server_default='manual', nullable=False))
    op.add_column('dividends', sa.Column('obsidian_imported', sa.Boolean(), server_default='false', nullable=False))

    # ── claim_records ──
    op.create_table('claim_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('holding_id', sa.Integer(), nullable=False),
        sa.Column('claim_reference', sa.String(length=100), nullable=True),
        sa.Column('claim_authority', sa.String(length=100), nullable=True),
        sa.Column('claim_type', sa.String(length=50), server_default='liquidation', nullable=False),
        sa.Column('date_filed', sa.Date(), nullable=True),
        sa.Column('date_acknowledged', sa.Date(), nullable=True),
        sa.Column('deadline_date', sa.Date(), nullable=True),
        sa.Column('claim_status', sa.String(length=30), server_default='pending', nullable=False),
        sa.Column('expected_payout', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('actual_payout', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('payout_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('documents_reference', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['holding_id'], ['holdings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("claim_status IN ('pending','approved','rejected','partially_paid','paid','lapsed')", name='chk_claim_status')
    )
    op.create_index('ix_claim_records_holding_id', 'claim_records', ['holding_id'], unique=False)
    op.create_index('ix_claim_records_claim_status', 'claim_records', ['claim_status'], unique=False)

    # ── obsidian_sync_log ──
    from sqlalchemy.dialects import postgresql
    op.create_table('obsidian_sync_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('run_by', sa.Integer(), nullable=True),
        sa.Column('vault_path', sa.Text(), nullable=False),
        sa.Column('companies_new', sa.Integer(), server_default='0', nullable=False),
        sa.Column('companies_skip', sa.Integer(), server_default='0', nullable=False),
        sa.Column('holdings_new', sa.Integer(), server_default='0', nullable=False),
        sa.Column('holdings_skip', sa.Integer(), server_default='0', nullable=False),
        sa.Column('dividends_new', sa.Integer(), server_default='0', nullable=False),
        sa.Column('dividends_skip', sa.Integer(), server_default='0', nullable=False),
        sa.Column('errors', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=True),
        sa.Column('run_mode', sa.String(length=20), server_default='manual', nullable=False),
        sa.ForeignKeyConstraint(['run_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('obsidian_sync_log')
    op.drop_index('ix_claim_records_claim_status', table_name='claim_records')
    op.drop_index('ix_claim_records_holding_id', table_name='claim_records')
    op.drop_table('claim_records')
    
    op.drop_column('dividends', 'obsidian_imported')
    op.drop_column('dividends', 'source')
    op.drop_column('dividends', 'payment_status')
    op.drop_column('dividends', 'dividend_type')
    
    op.drop_column('companies', 'obsidian_imported')
    op.drop_constraint('uq_companies_obsidian_slug', 'companies', type_='unique')
    op.drop_column('companies', 'obsidian_slug')
    op.drop_constraint('companies_status_check', 'companies', type_='check')
    op.create_check_constraint('chk_status', 'companies', "status IN ('listed','merged','defunct','delisted')")
    
    op.drop_column('holdings', 'obsidian_last_synced')
    op.drop_column('holdings', 'obsidian_imported')
    op.drop_column('holdings', 'cost_basis_override')
    op.drop_column('holdings', 'holding_type')
