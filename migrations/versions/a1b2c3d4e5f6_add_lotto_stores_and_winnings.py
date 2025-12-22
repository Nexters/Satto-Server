"""add lotto_stores and lotto_store_winnings tables

Revision ID: a1b2c3d4e5f6
Revises: 50ef02f95f5c
Create Date: 2025-12-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '50ef02f95f5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # lotto_stores 테이블 생성
    op.create_table(
        'lotto_stores',
        sa.Column('id', sa.String(length=20), nullable=False, comment='판매점 ID (RTLRID)'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='판매점 이름'),
        sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True, comment='위도'),
        sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True, comment='경도'),
        sa.Column('road_address', sa.String(length=200), nullable=True, comment='도로명주소'),
        sa.Column('lot_address', sa.String(length=100), nullable=True, comment='지번주소'),
        sa.Column('region1', sa.String(length=20), nullable=True, comment='시/도'),
        sa.Column('region2', sa.String(length=30), nullable=True, comment='시/군/구'),
        sa.Column('region3', sa.String(length=20), nullable=True, comment='동/읍/면'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='전화번호'),
        sa.Column('first_prize_count', sa.Integer(), nullable=True, default=0, comment='1등 배출 횟수'),
        sa.Column('first_prize_auto', sa.Integer(), nullable=True, default=0, comment='1등 자동 횟수'),
        sa.Column('first_prize_manual', sa.Integer(), nullable=True, default=0, comment='1등 수동 횟수'),
        sa.Column('first_prize_semi', sa.Integer(), nullable=True, default=0, comment='1등 반자동 횟수'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # region1, region2 인덱스 생성
    op.create_index('ix_lotto_stores_region1', 'lotto_stores', ['region1'], unique=False)
    op.create_index('ix_lotto_stores_region2', 'lotto_stores', ['region2'], unique=False)
    
    # lotto_store_winnings 테이블 생성
    op.create_table(
        'lotto_store_winnings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('store_id', sa.String(length=20), nullable=False, comment='판매점 ID'),
        sa.Column('round', sa.Integer(), nullable=False, comment='당첨 회차'),
        sa.Column('prize_rank', sa.Integer(), nullable=False, comment='당첨 등수 (1 또는 2)'),
        sa.Column('prize_type', sa.Enum('auto', 'manual', 'semi', name='prizetype'), nullable=True, comment='당첨 유형'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['store_id'], ['lotto_stores.id'], ),
        sa.ForeignKeyConstraint(['round'], ['lotto_draws.round'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # store_id, round 인덱스 생성
    op.create_index('ix_lotto_store_winnings_store_id', 'lotto_store_winnings', ['store_id'], unique=False)
    op.create_index('ix_lotto_store_winnings_round', 'lotto_store_winnings', ['round'], unique=False)
    
    # 복합 인덱스 생성
    op.create_index('ix_winning_round_rank', 'lotto_store_winnings', ['round', 'prize_rank'], unique=False)
    op.create_index('ix_winning_store_rank', 'lotto_store_winnings', ['store_id', 'prize_rank'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 인덱스 삭제
    op.drop_index('ix_winning_store_rank', table_name='lotto_store_winnings')
    op.drop_index('ix_winning_round_rank', table_name='lotto_store_winnings')
    op.drop_index('ix_lotto_store_winnings_round', table_name='lotto_store_winnings')
    op.drop_index('ix_lotto_store_winnings_store_id', table_name='lotto_store_winnings')
    
    # lotto_store_winnings 테이블 삭제
    op.drop_table('lotto_store_winnings')
    
    # lotto_stores 인덱스 삭제
    op.drop_index('ix_lotto_stores_region2', table_name='lotto_stores')
    op.drop_index('ix_lotto_stores_region1', table_name='lotto_stores')
    
    # lotto_stores 테이블 삭제
    op.drop_table('lotto_stores')
    
    # MySQL은 ENUM이 컬럼과 함께 삭제되므로 별도 처리 불필요

