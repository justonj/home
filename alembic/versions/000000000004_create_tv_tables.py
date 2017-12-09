'''Create TV tables'''

# revision identifiers, used by Alembic.
revision = '000000000004'
down_revision = '000000000003'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE tv_genres (
        tv_genre TEXT PRIMARY KEY,
        gracenote_name VARCHAR
    );
    ''')
    op.execute('CREATE INDEX ON tv_genres (tv_genre);')

    op.execute('''
    CREATE TABLE tv_show_names (
        tv_show_name TEXT,
        gracenote_name VARCHAR
    );
    ''')
    op.execute('CREATE INDEX ON tv_show_names (tv_show_name);')

    op.execute('''
    CREATE TABLE tv_channel_names (
        tv_channel_name TEXT,
        gracenote_name VARCHAR
    );
    ''')
    op.execute('CREATE INDEX ON tv_channel_names (tv_channel_name);')

    op.execute('''
    CREATE TABLE tv_types (
        tv_type TEXT PRIMARY KEY,
        gracenote_name TEXT
    );
    ''')

    op.execute('''
    CREATE TABLE tv_service_names (
        service_name TEXT PRIMARY KEY,
        gracenote_name TEXT
    );
    ''')


def downgrade():
    op.execute('DROP TABLE tv_genres;')
    op.execute('DROP TABLE tv_show_names;')
    op.execute('DROP TABLE tv_channel_names;')
    op.execute('DROP TABLE tv_types;')
    op.execute('DROP TABLE tv_service_names;')
