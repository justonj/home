import json
import os

import pytest
import requests_mock

from nlu.dialogue_system.test_utils import \
    assert_deterministic_conversation_features, \
    assert_deterministic_conversation_and_preformatted_queries
from nlu.dialogue_system.test_utils import create_payload, \
    create_expected_output, add_dialogue_rules_from_csv
from nlu.skills.skill_manager import get_skill


play_hello_response = open(pytest.SAMPLE_DATA_PATH +
                           "/music/music_play_hello.json").read()
proactive_hints_query = open(pytest.QUERIES_PATH +
                             '/queries_proactive_hints.json').read()
proactive_hints_response = open(pytest.SAMPLE_DATA_PATH +
                           "/music/proactive_hints.json").read()


MUSIC_SKILL_URL = get_skill('music').url + '/retrieve'
PROACTIVE_SKILL_URL = get_skill('proactive').url + '/retrieve'


@requests_mock.Mocker(kw='mock')
class TestCorrection:
    drm = None
    model_name = 'blank_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'correction.csv'),
            self.model_name,
            self.drm
        )
        self.drm.add_intent_dialogue_rule(
            'music_play', 'Boom, here you go', None)

    def teardown_class(self):
        self.drm.clear_rules()

    def test_correction_song_context(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
            create_expected_output('Boom, here you go'),

            (create_payload('Play Beat it'), 'music_play', {'song': 'beat it'}),
            create_expected_output('Boom, here you go'),

            (create_payload('no i meant the song'), 'correction',
             {'new_value': 'the song'}),
            create_expected_output(
                "Here's what I found for beat it: beat it by michael jackson "
                'and beat it by sean kingston. Which one do you want?'
            ),

            (create_payload('michael jackson'), 'correction', {}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "song":{
                        "album": {
                            "artist": {
                                "id": '88',
                                "name": "michael jackson",
                                "popularity": 0.83,
                                "type": "music_artist"
                            },
                            "id": '1056894',
                            "name": "history - past present and future - book i",
                            "type": "music_album"
                        },
                        "id": '11614332',
                        "name": "beat it",
                        "popularity": 0.49,
                        "user_input": "beat it",
                        "spoken_name": "beat it by michael jackson",
                        "type": "music_track"
                    }
                }
            )
        )

    def test_correction_playable_context(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'playable': 'hello'}),
            create_expected_output('Boom, here you go'),

            (create_payload('Play Beat it'), 'music_play',
             {'playable': 'beat it'}),
             create_expected_output('Boom, here you go'),

            (create_payload('no i meant the song'), 'correction',
             {'new_value': 'the song'}),
            create_expected_output(
                "Here's what I found for beat it: beat it by michael jackson "
                'and beat it by sean kingston. Which one do you want?'
            ),

            (create_payload('michael jackson'), 'correction', {}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "song":{
                        "album": {
                            "artist": {
                                "id": '88',
                                "name": "michael jackson",
                                "popularity": 0.83,
                                "type": "music_artist"
                            },
                            "id": '1056894',
                            "name": "history - past present and future - book i",
                            "type": "music_album"
                        },
                        "id": '11614332',
                        "name": "beat it",
                        "popularity": 0.49,
                        "user_input": "beat it",
                        "spoken_name": "beat it by michael jackson",
                        "type": "music_track"
                    }
                }
            )
        )

    def test_correction_artist_multiple_inputs(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello by adele'), 'music_play',
             {'song': 'hello', 'artist': 'adele'}),
            create_expected_output('Boom, here you go'),

            (create_payload('no i meant water under the bridge'), 'correction',
             {'new_value':'water under the bridge'}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "song":{
                        "album": {
                            "artist": {
                                "id": '142111',
                                "name": "adele",
                                "popularity": 0.84,
                                "type": "music_artist"
                            },
                            "id": '4944699',
                            "name": "25",
                            "type": "music_album"
                        },
                        "id": '50206250',
                        "name": "water under the bridge",
                        "popularity": 0.36,
                        "user_input": "water under the bridge",
                        "spoken_name": "water under the bridge by adele",
                        "type": "music_track"
                    },
                    "artist":{
                        "id": '142111',
                        "name": "adele",
                        "user_input": "adele",
                        "popularity": 0.84,
                        "type": "music_artist"
                    }
                }
            )
        )

    def test_correction_song_unresolved(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
            create_expected_output('Boom, here you go'),

            (create_payload('no i meant send my love'), 'correction',
             {'new_value':'send my love'}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "song":{
                        "type": "unresolved",
                        "user_input": "send my love",
                        "name": "send my love"
                    }
                }
            )
        )

    def test_correction_song_by_artist_candidate_match(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
            create_expected_output('Boom, here you go'),

            (create_payload('no i meant the one by adele'), 'correction',
             {'new_value':'adele'}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "song":{
                        "album": {
                            "artist": {
                                "id": '142111',
                                "name": "adele",
                                "popularity": 0.84,
                                "type": "music_artist"
                            },
                            "id": '4872748',
                            "name": "hello",
                            "type": "music_album"
                        },
                        "id": '49422899',
                        "name": "hello",
                        "popularity": 0.55,
                        "spoken_name": "hello by adele",
                        "user_input": "hello",
                        "type": "music_track"
                    }
                }
            )
        )

    def test_correction_song_no_candidate_match(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
            create_expected_output('Boom, here you go'),

            (create_payload('no i meant thriller'), 'correction',
             {'new_value':'thriller'}),
            create_expected_output(
                "Here's what I found for thriller: thriller by michael "
                'jackson, thriller by fall out boy and thriller by '
                'soundsense. Which one do you want?'
            ),

            (create_payload('fall out boy'), 'correction', {}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "song":{
                        "album": {
                            "artist": {
                                "id": '8860',
                                "name": "fall out boy",
                                "popularity": 0.75,
                                "type": "music_artist"
                            },
                            "id": '69021',
                            "name": "infinity on high",
                            "type": "music_album"
                        },
                        "id": '722046',
                        "name": "thriller",
                        "popularity": 0.37,
                        "user_input": "thriller",
                        "spoken_name": "thriller by fall out boy",
                        "type": "music_track"
                    }
                }
            )
        )

    def test_correction_song_to_album_trigger(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
            create_expected_output('Boom, here you go'),

            (create_payload('no i meant album'), 'correction',
             {'new_value':'album'}),
            create_expected_output(
                "Here's what I found for hello: hello by adele, hello by "
                'martin solveig, hello by joe, hello by karmin and hello by '
                'walk off the earth. Which one do you want?'
            ),

            (create_payload('martin solveig'), 'correction', {}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "album":{
                        "artist": {
                            "id": '6077',
                            "name": "martin solveig",
                            "popularity": 0.68,
                            "type": "music_artist"
                        },
                        "id": '1092797',
                        "name": "hello",
                        "user_input": "hello",
                        "spoken_name": "hello by martin solveig",
                        "type": "music_album"
                    }
                }
            )
        )

    def test_correction_playable_resolved(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_features(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'playable': 'hello'}),
            create_expected_output('Boom, here you go'),

            (create_payload('no i meant thriller'), 'correction',
             {'new_value':'thriller'}),
            create_expected_output(
                'Boom, here you go', intent='music_play',
                fields={
                    "album": {
                        "artist": {
                            "id": '88',
                            "name": "michael jackson",
                            "popularity": 0.83,
                            "type": "music_artist"
                        },
                        "id": '282494',
                        "name": "thriller",
                        "type": "music_album",
                        "casted": False,
                        "resolve_type": "knowledge_resolution",
                        "score": 0.83,
                        'spoken_name': 'thriller by michael jackson',
                        'user_input': 'thriller'
                     }
                }
            )
        )

    def test_correction_song_to_album_trigger_after_preformatted(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )
        m.register_uri(
            'POST',
            PROACTIVE_SKILL_URL,
            text=proactive_hints_response
        )

        assert_deterministic_conversation_and_preformatted_queries(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'song': 'hello'},
             False),
            create_expected_output('Boom, here you go'),

            (json.loads(proactive_hints_query), True),
            create_expected_output(''),

            (create_payload('no i meant album'), 'correction',
             {'new_value':'album'}, False),
            create_expected_output(
                "Here's what I found for hello: hello by adele, hello by "
                'martin solveig, hello by joe, hello by karmin and hello by '
                'walk off the earth. Which one do you want?'
            ),
        )

    def test_correction_playable_resolved_after_preformatted(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )
        m.register_uri(
            'POST',
            PROACTIVE_SKILL_URL,
            text=proactive_hints_response
        )

        assert_deterministic_conversation_and_preformatted_queries(
            self.model_name,
            self.drm,
            None,

            (create_payload('Play Hello'), 'music_play', {'playable': 'hello'},
             False),
            create_expected_output('Boom, here you go'),

            (json.loads(proactive_hints_query), True),
            create_expected_output(''),

            (create_payload('no i meant thriller'), 'correction',
             {'new_value':'thriller'}, False),
            create_expected_output('Boom, here you go', intent='music_play')
        )
