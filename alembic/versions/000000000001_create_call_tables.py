'''Create tables calltype, call_history_type'''

# revision identifiers, used by Alembic.
revision = '000000000001'
down_revision = '000000000000'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE call_history_type (
        call_history_type TEXT,
        value TEXT
    );
    ''')

    op.execute('''
    CREATE TABLE calltype (
        calltype TEXT,
        value TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE call_history_type;')
    op.execute('DROP TABLE calltype;')