'''Create table weather_condition'''

# revision identifiers, used by Alembic.
revision = '000000000009'
down_revision = '000000000008'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE weather_condition (
        weather_condition text,
        value text
    );
    ''')


def downgrade():
    op.execute('DROP TABLE weather_condition;')
