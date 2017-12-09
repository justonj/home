'''Create table sports_teams'''

# revision identifiers, used by Alembic.
revision = '000000000010'
down_revision = '000000000009'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE sports_teams (
        team TEXT,
        league TEXT,
        sport TEXT,
        country TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE sports_teams;')
