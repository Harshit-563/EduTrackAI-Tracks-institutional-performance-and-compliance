"""Create initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create institutions table
    op.create_table(
        'institutions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('total_students', sa.Integer(), nullable=True),
        sa.Column('total_faculty', sa.Integer(), nullable=True),
        sa.Column('placement_rate', sa.Float(), nullable=True),
        sa.Column('fund_utilization', sa.Float(), nullable=True),
        sa.Column('infrastructure_area', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_institutions_name'),
    )
    op.create_index('idx_institutions_name', 'institutions', ['name'])
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Create submissions table
    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_code', sa.String(50), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('doc_type', sa.String(100), nullable=True),
        sa.Column('dss_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('flags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('extracted_fields', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('submission_code', name='uq_submissions_code'),
    )
    op.create_index('idx_submissions_institution_id', 'submissions', ['institution_id'])
    op.create_index('idx_submissions_status', 'submissions', ['status'])
    
    # Create review_actions table
    op.create_table(
        'review_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_review_actions_submission_id', 'review_actions', ['submission_id'])
    
    # Create auth_tokens table
    op.create_table(
        'auth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash', name='uq_auth_tokens_hash'),
    )
    op.create_index('idx_auth_tokens_user_id', 'auth_tokens', ['user_id'])
    op.create_index('idx_auth_tokens_expires_at', 'auth_tokens', ['expires_at'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('idx_auth_tokens_expires_at', 'auth_tokens')
    op.drop_index('idx_auth_tokens_user_id', 'auth_tokens')
    op.drop_table('auth_tokens')
    op.drop_index('idx_review_actions_submission_id', 'review_actions')
    op.drop_table('review_actions')
    op.drop_index('idx_submissions_status', 'submissions')
    op.drop_index('idx_submissions_institution_id', 'submissions')
    op.drop_table('submissions')
    op.drop_index('idx_users_email', 'users')
    op.drop_table('users')
    op.drop_index('idx_institutions_name', 'institutions')
    op.drop_table('institutions')
