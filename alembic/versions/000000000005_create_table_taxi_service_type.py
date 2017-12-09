'''Create table taxi_service_type'''

# revision identifiers, used by Alembic.
revision = '000000000005'
down_revision = '000000000004'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE taxi_service_type (
        taxi_service_type TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE taxi_service_type;')
