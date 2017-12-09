'''Create table us_postal_codes'''

# revision identifiers, used by Alembic.
revision = '000000000007'
down_revision = '000000000006'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE us_postal_codes (
        us_postal_code TEXT PRIMARY KEY,
        place_name TEXT,
        state TEXT
    );
    ''')
    op.execute('CREATE INDEX ON us_postal_codes (us_postal_code);')


def downgrade():
    op.execute('DROP TABLE us_postal_codes;')
