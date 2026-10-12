"""convert ticket enum values to lowercase

Revision ID: 6fe334b10a29
Revises: e46d7a959e15
Create Date: 2026-10-12 12:51:39.848445
"""

from typing import Sequence, Union
from alembic import op

revision: str = "6fe334b10a29"
down_revision: Union[str, Sequence[str], None] = "e46d7a959e15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def rename_enum_values(enum_name: str, values: list[tuple[str, str]]):
    for old_value, new_value in values:
        op.execute(
            f"ALTER TYPE {enum_name} " f"RENAME VALUE '{old_value}' TO '{new_value}'"
        )


def upgrade() -> None:
    """Convert PostgreSQL enum labels to lowercase."""

    rename_enum_values(
        "ticket_type",
        [
            ("INCIDENT", "incident"),
            ("SERVICE_REQUEST", "service_request"),
        ],
    )

    rename_enum_values(
        "ticket_status",
        [
            ("OPEN", "open"),
            ("IN_PROGRESS", "in_progress"),
            ("PENDING", "pending"),
            ("RESOLVED", "resolved"),
            ("CLOSED", "closed"),
        ],
    )

    rename_enum_values(
        "ticket_priority",
        [
            ("LOW", "low"),
            ("MEDIUM", "medium"),
            ("HIGH", "high"),
            ("CRITICAL", "critical"),
        ],
    )


def downgrade() -> None:
    """Restore PostgreSQL enum labels to uppercase."""

    rename_enum_values(
        "ticket_type",
        [
            ("incident", "INCIDENT"),
            ("service_request", "SERVICE_REQUEST"),
        ],
    )

    rename_enum_values(
        "ticket_status",
        [
            ("open", "OPEN"),
            ("in_progress", "IN_PROGRESS"),
            ("pending", "PENDING"),
            ("resolved", "RESOLVED"),
            ("closed", "CLOSED"),
        ],
    )

    rename_enum_values(
        "ticket_priority",
        [
            ("low", "LOW"),
            ("medium", "MEDIUM"),
            ("high", "HIGH"),
            ("critical", "CRITICAL"),
        ],
    )
