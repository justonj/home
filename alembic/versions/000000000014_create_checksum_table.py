'''Create checksums table'''

# revision identifiers, used by Alembic.
revision = '000000000014'
down_revision = '000000000013'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Column 'table_name' is used for table names in this database as well as
    # relations inside the 'nlu' database table 'entities'
    op.execute('''
    CREATE TABLE checksums (
        name TEXT PRIMARY KEY,
        checksum TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE checksums;')
