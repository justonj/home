'''Create table skills'''

# revision identifiers, used by Alembic.
revision = '000000000017'
down_revision = '000000000016'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE permissions (
		intent_id TEXT PRIMARY KEY,
        permissions TEXT
       );
    ''')


def downgrade():
    op.execute('DROP TABLE permissions;')
