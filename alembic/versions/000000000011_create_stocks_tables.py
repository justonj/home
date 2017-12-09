'''Create tables stock_names, market_names'''

# revision identifiers, used by Alembic.
revision = '000000000011'
down_revision = '000000000010'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE stock_names (
        stock_name TEXT,
        ticker VARCHAR,
        market_name VARCHAR
    );
    ''')
    op.execute('CREATE INDEX ON stock_names (stock_name);')

    op.execute('''
    CREATE TABLE market_names (
        market_name TEXT,
        symbol TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE stock_names;')
    op.execute('DROP TABLE market_names;')
