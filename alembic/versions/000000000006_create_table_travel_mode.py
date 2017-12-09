'''Create table travel_mode'''

# revision identifiers, used by Alembic.
revision = '000000000006'
down_revision = '000000000005'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE travel_mode (
        travel_mode TEXT,
        value TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE travel_mode;')
