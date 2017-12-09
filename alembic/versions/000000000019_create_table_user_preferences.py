'''Create table user_preferences'''

# revision identifiers, used by Alembic.
revision = '000000000019'
down_revision = '000000000018'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE user_preferences (
        user_id TEXT,
        nickname TEXT,
        first_name TEXT,
        last_name TEXT,
        music_genres JSONB NOT NULL DEFAULT '{}',
        music_artists JSONB NOT NULL DEFAULT '{}'
    );
    ''')

def downgrade():
    op.execute('DROP TABLE user_preferences;')
