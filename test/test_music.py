from copy import copy
import os

import json
import pytest
import requests_mock

from nlu.dialogue_system.test_utils import assert_conversation_features, \
    create_payload, create_expected_output, add_dialogue_rules_from_csv
from nlu.skills.skill_manager import get_skill
from nlu.dialogue_system.test_utils import assert_conversation_deterministic, \
    assert_deterministic_conversation_features, \
    assert_deterministic_conversation_features_with_options,\
    assert_context_conversation_deterministic_features, create_context


play_hello_response = open(pytest.SAMPLE_DATA_PATH +
                           "/music/music_play_hello.json").read()
play_hello_response_dict = json.loads(play_hello_response)


MUSIC_SKILL_URL = get_skill('music').url + '/retrieve'
CONCERT_SKILL_URL = get_skill('concert').url + '/retrieve'

play_justin_bieber_response = open(
    pytest.SAMPLE_DATA_PATH + "/music/music_play_justin_bieber.json").read()
play_justin_bieber_response_dict = json.loads(play_justin_bieber_response)

queries_responses = [
    (('Play Hello', 'music_play', {'song': 'hello'}),
     MUSIC_SKILL_URL, 'music_play_hello.json', 'Boom, here you go'),
    (('Play Hello', 'music_play', {'song': 'hello', 'artist': 'joe'}),
     MUSIC_SKILL_URL, 'skill_exception_201.json', 'I can\'t find the track hello'),
    (('show music similar to Madonna', 'music_info_similar_artists', {'artist': 'madonna'}),
     MUSIC_SKILL_URL, 'music_info_similar_artists.json', 'Check out these artists similar to madonna'),
    (('show music similar to Madonna', 'music_info_similar_artists', {'artist': 'madonna'}),
     MUSIC_SKILL_URL, 'skill_exception_209.json', 'I can\'t find similar artists for madonna'),
    (('show me albums by adele', 'music_albums', {'artist': 'adele'}),
     MUSIC_SKILL_URL, 'music_albums.json', 'Here\'s all of adele\'s albums'),
    (('show me albums by adele', 'music_albums', {'artist': 'adele'}),
     MUSIC_SKILL_URL, 'skill_exception_203.json', 'I can\'t find albums for adele'),
    (('add hello by adele to my classical playlist', 'music_collection_add',
        {'song': 'hello', 'artist': 'adele', 'collection': 'classical'}),
     MUSIC_SKILL_URL, 'music_collections.json', 'Added hello by adele to classical collection'),
    (('Find adele concerts', 'music_info_concerts', {'artist': 'adele'}),
     CONCERT_SKILL_URL, 'music_info_concerts.json', 'Searching for adele concerts'),
    (('Find drake concerts', 'music_info_concerts', {'artist': 'drake'}),
     CONCERT_SKILL_URL, 'skill_exception_207.json', 'I can\'t find concerts for drake')
]


def read_file(filename):
    return open(os.path.join(pytest.SAMPLE_DATA_PATH, "music", filename)).read()


@requests_mock.Mocker(kw='mock')
class TestIntents:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'music.csv'),
            self.model_name,
            self.drm
        )

    def teardown_class(self):
        self.drm.clear_rules()

    def test_music_intents(self, **kwargs):
        m = kwargs['mock']
        for query, url, response_file, expected_output in queries_responses:
            print('QUERY:', query)
            m.register_uri(
                'POST',
                url,
                text=read_file(response_file)
            )

            assert_conversation_deterministic(
                self.model_name,
                self.drm,
                query,
                expected_output)

    def test_music_collection_add(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            status_code=401
        )
        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,
            (create_payload('add hello by adele to classical playlist'),
                'music_collection_add',
             {'artist': 'adele', 'song': 'hello', 'collection': 'classical'}),
            create_expected_output(
                'I can\'t answer it now. Please try again',
                fields={
                   "http_error": {
                       'type': 'http_error',
                        'message': 'Skill error',
                        'name': 401
                     }
                })
        )

    def test_music_id(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )
        followup_program = play_hello_response_dict['fields']['tracks']['items'][0]
        assert_context_conversation_deterministic_features(
            self.model_name,
            self.drm,
            None,
            (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
            create_expected_output('Boom, here you go'),
            (create_payload('what song is this', display_context=create_context(list_id='hello_response', index_id='49422899')),
                            'music_id', {}),
            create_expected_output('This track is Hello')
        )

    def test_replay(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_justin_bieber_response
        )
        biebs_mention = {
            'artist': copy(play_justin_bieber_response_dict['fields']['tracks']['items'][0]['album']['artist'])
        }
        biebs_mention['artist']['name'] = biebs_mention['artist']['name'].lower()
        biebs_mention['artist']['user_input']= biebs_mention['artist']['name']
        biebs_tracks = play_justin_bieber_response_dict['fields']['tracks']
        tracks_mention = {
            'tracks': biebs_tracks
        }
        assert_deterministic_conversation_features_with_options(
            self.model_name,
            self.drm,
            (create_payload('Play justin bieber'),
             'music_play',
             {'artist': 'justin bieber'}),
            (
                True,
                create_expected_output(
                    'Boom, here you go',
                    fields={
                        "artist": biebs_mention["artist"],
                        "tracks": tracks_mention["tracks"]
                    }
                )
            ),
            (create_payload('play that songs again'),
             'music_replay',
             {}),
            (
                True,
                create_expected_output(
                    'Here is recent music you requested',
                    fields={
                        "tracks": {
                            "name": "",
                            "type": "list",
                            "items" : tracks_mention["tracks"]["items"]
                        }
                    }
                )
            )
        )
