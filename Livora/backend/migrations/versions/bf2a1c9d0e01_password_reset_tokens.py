"""password reset tokens

Revision ID: bf2a1c9d0e01
Revises: a9404d3027e0
Create Date: 2026-04-05

"""
import sqlalchemy as sa
from alembic import op

revision = "bf2a1c9d0e01"
down_revision = "a9404d3027e0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "password_reset_token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_password_reset_token_user_id", "password_reset_token", ["user_id"])
    op.create_index("ix_password_reset_token_token_hash", "password_reset_token", ["token_hash"])


def downgrade():
    op.drop_index("ix_password_reset_token_token_hash", table_name="password_reset_token")
    op.drop_index("ix_password_reset_token_user_id", table_name="password_reset_token")
    op.drop_table("password_reset_token")
