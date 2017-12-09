'''Create table skill_name'''

# revision identifiers, used by Alembic.
revision = '000000000002'
down_revision = '000000000001'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE skill_name (
        skill_name TEXT,
        value TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE skill_name;')
