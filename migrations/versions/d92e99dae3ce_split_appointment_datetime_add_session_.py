
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd92e99dae3ce'
down_revision: Union[str, None] = '611480e351bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ── Appointments ──────────────────────────────────────────────

    # Step 1: Add appointment_date as nullable first
    op.add_column('appointments', sa.Column('appointment_date', sa.Date(), nullable=True))
    op.add_column('appointments', sa.Column('notes', sa.Text(), nullable=True))

    # Step 2: Fill existing rows — extract date from old appointment_time
    op.execute("""
        UPDATE appointments
        SET appointment_date = appointment_time::date
        WHERE appointment_date IS NULL
    """)

    # Step 3: Now enforce NOT NULL
    op.alter_column('appointments', 'appointment_date', nullable=False)

    # Step 4: Convert appointment_time from TIMESTAMP to Time
    op.alter_column(
        'appointments', 'appointment_time',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.Time(),
        existing_nullable=False,
        postgresql_using='appointment_time::time'   # cast existing data
    )

    # Step 5: Widen reason from VARCHAR to Text (safe, no data loss)
    op.alter_column(
        'appointments', 'reason',
        existing_type=sa.VARCHAR(),
        type_=sa.Text(),
        existing_nullable=True
    )

    # ── Conversations ─────────────────────────────────────────────

    # Step 1: Add session_id as nullable first
    op.add_column('conversations', sa.Column('session_id', sa.String(), nullable=True))

    # Step 2: Fill existing rows with a legacy value
    op.execute("""
        UPDATE conversations
        SET session_id = 'legacy-' || id::text
        WHERE session_id IS NULL
    """)

    # Step 3: Now enforce NOT NULL
    op.alter_column('conversations', 'session_id', nullable=False)

    # Step 4: Create index
    op.create_index(
        op.f('ix_conversations_session_id'),
        'conversations',
        ['session_id'],
        unique=False
    )

    # Step 5: Drop metadata column
    op.drop_column('conversations', 'metadata')


def downgrade() -> None:
    # Restore metadata column
    op.add_column('conversations',
        sa.Column('metadata', sa.TEXT(), autoincrement=False, nullable=True)
    )

    # Remove session_id
    op.drop_index(op.f('ix_conversations_session_id'), table_name='conversations')
    op.drop_column('conversations', 'session_id')

    # Revert appointments
    op.alter_column(
        'appointments', 'reason',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )
    op.alter_column(
        'appointments', 'appointment_time',
        existing_type=sa.Time(),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        postgresql_using='appointment_time::timestamp'
    )
    op.drop_column('appointments', 'notes')
    op.drop_column('appointments', 'appointment_date')