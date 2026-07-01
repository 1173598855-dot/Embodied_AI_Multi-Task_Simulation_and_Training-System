"""initial enterprise foundation schema

Revision ID: 20260701_initial
Revises:
Create Date: 2026-07-01
"""

from alembic import op
import sqlalchemy as sa

revision = "20260701_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("env_type", sa.String(length=32), nullable=False, server_default="gym"),
        sa.Column("env_name", sa.String(length=64), nullable=False, server_default="CartPole-v1"),
        sa.Column("algo", sa.String(length=32), nullable=False, server_default="q_learning"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="created"),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("total_reward", sa.Float(), nullable=True),
        sa.Column("current_run_id", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_current_run_id", "tasks", ["current_run_id"])

    op.create_table(
        "training_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=True),
        sa.Column("episode", sa.Integer(), nullable=False),
        sa.Column("step", sa.Integer(), nullable=False),
        sa.Column("reward", sa.Float(), nullable=False),
        sa.Column("avg_reward", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_training_logs_task_id", "training_logs", ["task_id"])
    op.create_index("ix_training_logs_run_id", "training_logs", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_training_logs_run_id", table_name="training_logs")
    op.drop_index("ix_training_logs_task_id", table_name="training_logs")
    op.drop_table("training_logs")
    op.drop_index("ix_tasks_current_run_id", table_name="tasks")
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_table("tasks")
