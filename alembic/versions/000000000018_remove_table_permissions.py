'''Remove table permissions'''

# revision identifiers, used by Alembic.
revision = '000000000018'
down_revision = '000000000017'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('DROP TABLE permissions;')

def downgrade():
    op.execute('''
    CREATE TABLE permissions (
	intent_id TEXT PRIMARY KEY,
        permissions TEXT
       );
    ''')

