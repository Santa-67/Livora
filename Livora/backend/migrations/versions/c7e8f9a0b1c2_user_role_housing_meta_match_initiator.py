"""user role, property housing_meta, match initiator

Revision ID: c7e8f9a0b1c2
Revises: bf2a1c9d0e01
Create Date: 2026-04-06

"""
import sqlalchemy as sa
from alembic import op

revision = "c7e8f9a0b1c2"
down_revision = "bf2a1c9d0e01"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("role", sa.String(length=20), nullable=False, server_default="tenant")
        )
    with op.batch_alter_table("property", schema=None) as batch_op:
        batch_op.add_column(sa.Column("housing_meta", sa.JSON(), nullable=True))
    with op.batch_alter_table("match", schema=None) as batch_op:
        batch_op.add_column(sa.Column("initiator_id", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("match", schema=None) as batch_op:
        batch_op.drop_column("initiator_id")
    with op.batch_alter_table("property", schema=None) as batch_op:
        batch_op.drop_column("housing_meta")
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("role")
