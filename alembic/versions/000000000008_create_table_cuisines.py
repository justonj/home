'''Create table cuisines'''

# revision identifiers, used by Alembic.
revision = '000000000008'
down_revision = '000000000007'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE cuisines (
        cuisine_name TEXT PRIMARY KEY,
        yelp_input TEXT
    );
    ''')
    op.execute('CREATE INDEX ON cuisines (cuisine_name);')


def downgrade():
    op.execute('DROP TABLE cuisines;')
