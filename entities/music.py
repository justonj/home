import psycopg2
import os

import nlu.knowledge_base.knowledge_base_helpers as helpers
from nlu.knowledge_base.entity_type_registry import register_entity_type, \
    EntityType
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from nlu.knowledge_base.entity_types import DatabaseEntityType
from nlu.postgres_utils import AppCursor
from config import config


def _get_spoken_name(song_or_album_name, artist_name):
    if artist_name is None:
        return song_or_album_name
    else:
        return (song_or_album_name or '') + ' by ' + artist_name


def sort_candidates_by_score(candidates, entity_type_name):
    entity_type = EntityType(entity_type_name)
    candidates.sort(reverse=True, key=lambda c: entity_type.score(c))


def _filtered_candidates_by_mentioned_artist(candidates, mentions):
    for mention in mentions:
        if mention.type_name == 'music_artist':
            if mention.has_entity():
                artist_id = mention.entity.get('id')
                if artist_id:
                    matches = [c for c in candidates
                               if artist_id == c.get('album', c)['artist']['id']]
                    if matches:
                        return matches
                if mention.entity_value:
                    artist_name = mention.entity_value
            else:
                artist_name = mention.value

            matches = [c for c in candidates
                       if artist_name == c.get('album', c)['artist']['name']]
            return matches
    return candidates


def _formatted_unique_candidates(candidates, entity_type_name):
    formatted_candidates = []
    spoken_names = set()
    for candidate in candidates:
        candidate = candidate.get('entity', candidate)
        artist_name = candidate.get('album', candidate)['artist']['name']
        album_name = candidate.get('album', candidate).get('name')
        spoken_name = _get_spoken_name(candidate['name'],
                                       artist_name)
        if spoken_name not in spoken_names:
            candidate['spoken_name'] = spoken_name
            spoken_names.add(spoken_name)
            formatted_candidates.append(candidate)
    sort_candidates_by_score(formatted_candidates, entity_type_name)
    return formatted_candidates


class MusicArtistType(EntityTypeBase):
    id = 'music_artist'
    POPULARITY_THRESHOLD = 0.5
    HEAD_VALUES_PATH = os.path.join(config.RAW_KNOWLEDGE_DIR, id + 's.head')

    def has_data(self):
        return helpers.table_has_data('music_artists')

    def rebuild(self, filename):
        return helpers.import_csv(filename, 'music_artists', [1])

    def update(self, filename):
        # For now, just delete and re-import the data. Later, we should
        # build some sort of incremental update.
        helpers.delete_all_in_table('music_artists')
        self.rebuild(filename)

    def all_values(self):
        with AppCursor() as cur:
            try:
                cur.execute('SELECT name FROM music_artists WHERE popularity > %s;',
                            [self.POPULARITY_THRESHOLD])
                for row in cur:
                    yield row[0]
            except psycopg2.ProgrammingError as e:
                print(e)
                pass

    def from_id(self, id_):
        if id_ is not None:
            artists = self.get_candidates(id_, 'id')
            if len(artists) == 1:
                return artists[0]

    def from_name(self, name):
        artists = self.get_candidates(name.lower(), 'name')
        if len(artists) == 1:
            return artists[0]

    def get_candidates(self, text, column_name='name', **kwargs):
        matches = helpers.find_all_exact_match(
            'music_artists',
            column_name,
            text,
            ['id', 'name', 'popularity'],
            value_column='name'
        )
        return [
            {
                'id': match['id'],
                'name': match['name'],
                'popularity': match['popularity'],
                'type': self.id
            }
            for match in matches
        ]

    def score(self, entity):
        return entity.get('popularity') or 0

    @classmethod
    def head_values(cls):
        with open(cls.HEAD_VALUES_PATH) as head_values_file:
            for line in head_values_file:
                yield line.strip()


class MusicTrackType(EntityTypeBase):
    id = 'music_track'
    db_column_names = ['id', 'name', 'popularity', 'album_id', 'album_name',
                       'artist_id', 'artist_name', 'artist_popularity']
    HEAD_VALUES_PATH = os.path.join(config.RAW_KNOWLEDGE_DIR, id + 's.head')

    def has_data(self):
        return helpers.table_has_data('music_tracks')

    def rebuild(self, filename):
        return helpers.import_csv(filename, 'music_tracks', [2])

    def update(self, filename):
        # For now, just delete and re-import the data. Later, we should
        # build some sort of incremental update.
        helpers.delete_all_in_table('music_tracks')
        self.rebuild(filename)

    def prepare_candidates(self, candidates, user, mentions):
        """
        Return a list of music tracks from the 5 most popular known tracks in `candidates`. If an artist was mentioned
        by the user, restrict the results to tracks by the last artist mentioned. A mention is a dict with key
        `field_id`, and an artist mention has value `'artist'` for that key. Add the key `spoken_name` to each music
        track dict returned.

        :param candidates: List of dicts representing previously matched music tracks to select from
        :param user: Not used
        :param mentions: List of dicts representing recognized items user in user's response after `candidates` were matched
        :return A list of tracks from `candidates` matching the last artist mentioned by the user, if any
        """
        candidates = _filtered_candidates_by_mentioned_artist(candidates, mentions)
        return _formatted_unique_candidates(candidates[:5], self.id)

    def get_candidates(self, text, **kwargs):
        matches = helpers.find_all_exact_match(
            'music_tracks_albums_artists',
            'name',
            text,
            self.db_column_names,
        )
        return [
            {
                'id': match['id'],
                'name': match['name'],
                'popularity': match['popularity'],
                'type': self.id,
                'album': MusicAlbumType.from_db_match(match['album_id'],
                                                      match['album_name'],
                                                      match)
            }
            for match in matches
        ]

    def score(self, entity):
        track_popularity = entity.get('popularity')
        if track_popularity:
            return track_popularity
        return entity.get('artist', {}).get('popularity') or 0

    @classmethod
    def head_values(cls):
        with open(cls.HEAD_VALUES_PATH) as head_values_file:
            for line in head_values_file:
                yield line.strip()

    def all_values(self):
        with AppCursor() as cur:
            try:
                cur.execute('SELECT name FROM music_tracks;')
                for row in cur:
                    yield row[0]
            except psycopg2.ProgrammingError as e:
                print(e)
                pass


class MusicAlbumType(DatabaseEntityType):
    id = 'music_album'
    db_table_name = 'music_albums'

    def __init__(self):
        DatabaseEntityType.__init__(
            self,
            'music_album',
            'music_albums',
            'name',
            [2],
            ['artist_id', 'name'])

    def has_data(self):
        return helpers.table_has_data(self.db_table_name)

    def rebuild(self, filename):
        return helpers.import_csv(filename, self.db_table_name, [2])

    def update(self, filename):
        helpers.delete_all_in_table(self.db_table_name)
        self.rebuild(filename)

    def from_id(self, id_):
        if id_ is not None:
            candidates = self.get_candidates(id_, 'id')
            if len(candidates) == 1:
                return candidates[0]

    @staticmethod
    def from_db_match(id, name, match):
        return {
            'id': id,
            'name': name,
            'type': "music_album",
            'artist': {
                'id': match['artist_id'],
                DEFAULT_VALUE_KEY: match['artist_name'],
                'popularity': match['artist_popularity'],
                'type': 'music_artist'
            }
        }

    def get_candidates(self, text, column_name=None, **kwargs):
        matches = helpers.find_all_exact_match(
            'music_albums_artists',
            column_name or DEFAULT_VALUE_KEY,
            text,
            ['id', 'name', 'artist_id', 'artist_name', 'artist_popularity'],
        )
        return [
            self.from_db_match(match['id'], match['name'], match)
            for match in matches
        ]

    def prepare_candidates(self, candidates, user, mentions):
        """
        Return a list of music albums from `candidates`.  If an artist was
        mentioned by the user, restrict the results to albums by the last artist
        mentioned.

        :param candidates: List of dicts representing previously matched music
            albums to select from
        :param user: Not used
        :param mentions: List of dicts representing recognized items user in
            user's response after `candidates` were matched. A mention has a key
            `field_id`, and an artist mention has value `'artist'` for that key.
        :return A list of elements from `candidates` matching the last artist
            mentioned by the user, if any, with an additional key `spoken name`.
        """
        candidates = _filtered_candidates_by_mentioned_artist(candidates,
                                                              mentions)
        return _formatted_unique_candidates(candidates[:5], self.id)

    def score(self, entity):
        return entity.get('artist', {}).get('popularity') or 0


register_entity_type(MusicTrackType())
register_entity_type(MusicArtistType())
register_entity_type(MusicAlbumType())
