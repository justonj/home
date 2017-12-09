'''Create table user_email_contacts'''

# revision identifiers, used by Alembic.
revision = '000000000000'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE user_email_contacts (
        userId TEXT,
        accountType TEXT,
        accountId TEXT,
        searchKey TEXT,
        data JSONB NOT NULL DEFAULT '{}');
    ''')


def downgrade():
    op.execute('DROP TABLE user_email_contacts;')
