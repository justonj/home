"""change_music_id_type.py

Revision ID: 000000000014
Revises: 000000000014
Create Date: 2017-06-14 15:37:15.350905
"""

# revision identifiers, used by Alembic.
revision = '000000000016'
down_revision = '000000000015'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa



def upgrade():
    drop_views()
    drop_foreign_key_constraints()
    op.execute("""
        ALTER TABLE music_artists ALTER COLUMN id TYPE TEXT;
        """)
    op.execute("""
        ALTER TABLE music_albums ALTER COLUMN id TYPE TEXT;
        """)
    op.execute("""
        ALTER TABLE music_albums ALTER COLUMN artist_id TYPE TEXT
        """)
    op.execute("""
        ALTER TABLE music_tracks ALTER COLUMN id TYPE TEXT;
        """)
    op.execute("""
        ALTER TABLE music_tracks ALTER COLUMN artist_id TYPE TEXT;
        """)
    op.execute("""
        ALTER TABLE music_tracks ALTER COLUMN album_id TYPE TEXT;
        """)
    op.execute("""
        ALTER TABLE music_eras ALTER COLUMN id TYPE TEXT;
        """)
    op.execute("""
        ALTER TABLE music_moods ALTER COLUMN id TYPE TEXT;
        """)
    op.execute("""
        ALTER TABLE music_genres ALTER COLUMN id TYPE TEXT;
        """)
    create_foreign_key_constraints()
    create_views()
    


def downgrade():
    drop_views()
    drop_foreign_key_constraints()
    op.execute("""
        ALTER TABLE music_artists ALTER COLUMN id TYPE INTEGER USING (id::integer);
        """)
    op.execute("""
        ALTER TABLE music_albums ALTER COLUMN id TYPE INTEGER USING (id::integer);
        """)
    op.execute("""
        ALTER TABLE music_albums ALTER COLUMN artist_id TYPE INTEGER USING (artist_id::integer);
        """)
    op.execute("""
        ALTER TABLE music_tracks ALTER COLUMN id TYPE INTEGER USING (id::integer);
        """)
    op.execute("""
        ALTER TABLE music_tracks ALTER COLUMN artist_id TYPE INTEGER USING (artist_id::integer);
        """)
    op.execute("""
        ALTER TABLE music_tracks ALTER COLUMN album_id TYPE INTEGER USING (album_id::integer);
        """)
    op.execute("""
        ALTER TABLE music_eras ALTER COLUMN id TYPE INTEGER USING (id::integer);
        """)
    op.execute("""
        ALTER TABLE music_moods ALTER COLUMN id TYPE INTEGER USING (id::integer);
        """)
    op.execute("""
        ALTER TABLE music_genres ALTER COLUMN id TYPE INTEGER USING (id::integer);
        """)
    create_foreign_key_constraints()
    create_views()


def drop_foreign_key_constraints():
    op.execute("""
        ALTER TABLE music_albums 
        DROP CONSTRAINT music_albums_artist_id_fkey
        """)
    op.execute("""
        ALTER TABLE music_tracks 
        DROP CONSTRAINT music_tracks_artist_id_fkey,
        DROP CONSTRAINT music_tracks_album_id_fkey
        """)

def create_foreign_key_constraints():
    op.execute("""
        ALTER TABLE music_albums 
        ADD CONSTRAINT music_albums_artist_id_fkey FOREIGN KEY (artist_id) REFERENCES music_artists (id) ON DELETE CASCADE;
        """)
    op.execute("""
        ALTER TABLE music_tracks 
        ADD CONSTRAINT music_tracks_artist_id_fkey FOREIGN KEY (artist_id) REFERENCES music_artists (id) ON DELETE CASCADE;
        """)
    op.execute("""
        ALTER TABLE music_tracks
        ADD CONSTRAINT music_tracks_album_id_fkey FOREIGN KEY (album_id) REFERENCES music_albums (id) ON DELETE CASCADE;
        """)

def drop_views():
    op.execute('DROP VIEW music_tracks_albums_artists;')
    op.execute('DROP VIEW music_albums_artists;')
    for table_name in 'music_tracks', 'music_artists', 'music_albums':
        op.execute('''
        DROP INDEX %s_name_gin_trgm_idx;
        '''
        % (table_name))


def create_views():
    op.execute('''
    CREATE VIEW music_albums_artists AS
    SELECT
        music_albums.id,
        music_albums.name,
        music_artists.id artist_id,
        music_artists.name artist_name,
        music_artists.popularity artist_popularity
    FROM music_albums
    INNER JOIN music_artists ON music_albums.artist_id = music_artists.id
    ORDER BY artist_popularity DESC;
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
