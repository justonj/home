'''Create table skills'''

# revision identifiers, used by Alembic.
revision = '000000000015'
down_revision = '000000000014'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE skills (
        skill_id TEXT PRIMARY KEY,
        data JSONB NOT NULL DEFAULT '{}');
    ''')


def downgrade():
    op.execute('DROP TABLE skills;')
