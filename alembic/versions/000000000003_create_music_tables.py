'''Create music tables'''

# revision identifiers, used by Alembic.
revision = '000000000003'
down_revision = '000000000002'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('''
    CREATE TABLE music_artists (
        id integer PRIMARY KEY,
        name TEXT,
        popularity FLOAT
    );
    ''')
    op.execute('CREATE INDEX ON music_artists (name);')

    op.execute('''
    CREATE TABLE music_albums (
        id integer PRIMARY KEY,
        artist_id INTEGER REFERENCES music_artists (id) ON DELETE CASCADE,
        name TEXT
    );
    ''')
    op.execute('CREATE INDEX ON music_albums (name);')

    op.execute('''
    CREATE TABLE music_tracks (
        id INTEGER PRIMARY KEY,
        artist_id INTEGER REFERENCES music_artists (id) ON DELETE CASCADE,
        name TEXT,
        popularity FLOAT,
        album_id INTEGER REFERENCES music_albums (id) ON DELETE CASCADE
    );
    ''')
    op.execute('CREATE INDEX ON music_tracks (name);')
    op.execute('CREATE INDEX ON music_tracks (artist_id);')
    op.execute('CREATE INDEX ON music_tracks (album_id);')

    op.execute('''
    CREATE TABLE music_eras (
        name TEXT,
        gracenote_name TEXT,
        id INTEGER
    );
    ''')
    op.execute('CREATE INDEX ON music_eras (name);')

    op.execute('''
    CREATE TABLE music_moods (
        name TEXT,
        gracenote_name TEXT,
        id INTEGER
    );
    ''')
    op.execute('CREATE INDEX ON music_moods (name);')

    op.execute('''
    CREATE TABLE music_genres (
        name text,
        gracenote_name TEXT,
        id INTEGER
    );
    ''')
    op.execute('CREATE INDEX ON music_genres (name);')

    op.execute('''
    CREATE TABLE music_collections (
        music_collection TEXT PRIMARY KEY
    );
    ''')
    op.execute('CREATE INDEX ON music_collections (music_collection);')


def downgrade():
    op.execute('DROP TABLE music_tracks;')
    op.execute('DROP TABLE music_albums;')
    op.execute('DROP TABLE music_artists;')
    op.execute('DROP TABLE music_eras;')
    op.execute('DROP TABLE music_moods;')
    op.execute('DROP TABLE music_genres;')
    op.execute('DROP TABLE music_collections;')
