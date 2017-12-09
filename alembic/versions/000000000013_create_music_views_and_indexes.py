'''Create music views and indexes'''

# revision identifiers, used by Alembic.
revision = '000000000013'
down_revision = '000000000012'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

from config import config


def upgrade():
    op.execute('''
    CREATE VIEW music_albums_artists AS
    SELECT
        music_albums.id,
        music_albums.name,
        music_artists.id artist_id,
        music_artists.name artist_name,
        music_artists.popularity artist_popularity
    FROM music_albums
    INNER JOIN music_artists ON music_albums.artist_id = music_artists.id;
    ''')

    op.execute('''
    CREATE VIEW music_tracks_albums_artists AS
    SELECT
        music_tracks.id,
        music_tracks.name,
        music_tracks.popularity,
        music_albums.id album_id,
        music_albums.name album_name,
        music_artists.id artist_id,
        music_artists.name artist_name,
        music_artists.popularity artist_popularity
    FROM music_tracks
    INNER JOIN music_albums ON music_tracks.album_id = music_albums.id
    INNER JOIN music_artists ON music_albums.artist_id = music_artists.id
    ORDER BY popularity DESC, artist_popularity DESC;
    ''')

    try:
        for table_name in 'music_tracks', 'music_artists', 'music_albums':
            op.execute('''
            CREATE INDEX %s_name_gin_trgm_idx ON %s USING gin (name gin_trgm_ops);
            '''
            % (table_name, table_name))
    except sa.exc.ProgrammingError as e:
        if 'operator class "gin_trgm_ops" does not exist for access method "gin"' in e.args[0]:
            print('Please run the following command to create extension pg_trgm:')
            print('sudo -u postgres bash -c "psql -d %s -c \'CREATE EXTENSION pg_trgm;\'"' % config.PG_APP_DB)


def downgrade():
    op.execute('DROP VIEW music_tracks_albums_artists;')
    op.execute('DROP VIEW music_albums_artists;')
    for table_name in 'music_tracks', 'music_artists', 'music_albums':
        op.execute('''
        DROP INDEX %s_name_gin_trgm_idx;
        '''
        % (table_name))
