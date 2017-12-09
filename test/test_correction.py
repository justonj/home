import requests_mock
import pytest
import json
import os

from nlu.dialogue_system.test_utils import create_payload, create_expected_output, add_dialogue_rules_from_csv
from nlu.skills.skill_manager import get_skill
from nlu.dialogue_system.test_utils import assert_context_conversation_deterministic_features, create_context
from nlu.dialogue_system.test_utils import assert_deterministic_conversation_and_preformatted_queries

play_hello_response = open(pytest.SAMPLE_DATA_PATH +
                           "/music/music_play_hello.json").read()

MUSIC_SKILL_URL = get_skill('music').url + '/retrieve'
PROACTIVE_SKILL_URL = get_skill('proactive').url + '/retrieve'

proactive_hints_input = open(pytest.SAMPLE_DATA_PATH +
                           "/proactive/proactive_hints_input.json").read()

proactive_hints_input_dict = json.loads(proactive_hints_input)

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

        assert_context_conversation_deterministic_features(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
              create_expected_output('Boom, here you go'),
             (create_payload('Play Beat it',  display_context=create_context(list_id='hello_response', index_id='49422899')),
              'music_play', {'song': 'beat it'}),
              create_expected_output('Boom, here you go'),
             (create_payload('no not this one'), 'correction', {}),
              create_expected_output('Do you want beat it the song, artist or album?'),
             (create_payload('song'), 'correction', {'corrected_field':'song'}),
             create_expected_output('Here\'s what I found for beat it: beat it by michael jackson and beat it by sean kingston. Which one do you want?',
                                    intent='correction'),
             (create_payload('michael jackson'), 'correction', {'new_value':'michael jackson'}),
             create_expected_output('Boom, here you go', intent='music_play',
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
                            "user_input": "beat it",
                            "popularity": 0.49,
                            "spoken_name": "beat it by michael jackson",
                            "type": "music_track"
                        }
                    })
            )

    def test_correction_playable_context(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
          )

        assert_context_conversation_deterministic_features(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play Hello'), 'music_play', {'playable': 'hello'}),
              create_expected_output('Boom, here you go'),
             (create_payload('Play Beat it', display_context=create_context(list_id='hello_response', index_id='49422899')),
              'music_play', {'playable': 'beat it'}),
              create_expected_output('Boom, here you go'),
             (create_payload('no not this one'), 'correction', {}),
              create_expected_output('Do you want beat it the song, artist or album?'),
             (create_payload('song'), 'correction', {'corrected_field':'song'}),
             create_expected_output('Here\'s what I found for beat it: beat it by michael jackson and beat it by sean kingston. Which one do you want?',
                                    intent='correction'),
             (create_payload('michael jackson'), 'correction', {'new_value':'michael jackson'}),
             create_expected_output('Boom, here you go', intent='music_play',
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
                            "user_input": "beat it",
                            "popularity": 0.49,
                            "spoken_name": "beat it by michael jackson",
                            "type": "music_track"
                        }
                    })
            )

    def test_correction_song_to_album_candidates(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
          )

        assert_context_conversation_deterministic_features(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
              create_expected_output('Boom, here you go'),
             (create_payload('no not this one'), 'correction', {}),
              create_expected_output('Do you want hello the song, artist or album?'),
             (create_payload('album'), 'correction', {'corrected_field':'album'}),
             create_expected_output('Here\'s what I found for hello: hello by adele, hello by martin solveig, hello by joe, hello by karmin and hello by walk off the earth. Which one do you want?',
                                    intent='correction'),
             (create_payload('hello by karmin'), 'correction', {'new_value':'hello by karmin'}),
             create_expected_output('Boom, here you go', intent='music_play',
                    fields={
                        "album":{
                            "artist": {
                                "id": '818924',
                                "name": "karmin",
                                "popularity": 0.62,
                                "type": "music_artist"
                            },
                            "id": '1694211',
                            "name": "hello",
                            "user_input": "hello",
                            "spoken_name": "hello by karmin",
                            "type": "music_album"
                        }
                    })
            )

    def test_correction_song_to_song_candidates(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
          )

        assert_context_conversation_deterministic_features(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play Hello'), 'music_play', {'song': 'hello'}),
              create_expected_output('Boom, here you go'),
             (create_payload('no not this one'), 'correction', {}),
              create_expected_output('Do you want hello the song, artist or album?'),
             (create_payload('song'), 'correction', {'corrected_field':'song'}),
              create_expected_output('Here\'s what I found for hello: hello by adele, hello by j cole, hello by beyoncé, hello by joe and hello by eminem. Which one do you want?'),
             (create_payload('hello by adele'), 'correction', {'new_value':'hello by adele'}),
              create_expected_output('Boom, here you go', intent='music_play',
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
                            "user_input": "hello",
                            "popularity": 0.55,
                            "spoken_name": "hello by adele",
                            "type": "music_track"
                        }
                    })
            )

    def test_correction_song_to_song_no_candidates(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
          )

        assert_context_conversation_deterministic_features(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play man in the mirror'), 'music_play', {'song': 'man in the mirror'}),
              create_expected_output('Boom, here you go'),
             (create_payload('no not this one'), 'correction', {}),
              create_expected_output('Do you want man in the mirror the song, artist or album?'),
             (create_payload('song'), 'correction', {'corrected_field':'song'}),
              create_expected_output('Boom, here you go', intent='music_play',
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
                            "id": '11614324',
                            "name": "man in the mirror",
                            "user_input": "man in the mirror",
                            "popularity": 0.47,
                            "spoken_name": "man in the mirror by michael jackson",
                            "type": "music_track"
                        }
                    })
            )

    def test_correction_song_to_song_no_entity(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
          )

        assert_context_conversation_deterministic_features(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play man in the mirror back'), 'music_play', {'song': 'man in the mirror back'}),
              create_expected_output('Boom, here you go'),
             (create_payload('no not this one'), 'correction', {}),
              create_expected_output('Do you want man in the mirror back the song, artist or album?'),
             (create_payload('song'), 'correction', {'corrected_field':'song'}),
              create_expected_output('Boom, here you go', intent='music_play',
                    fields={
                        "song":{
                            "type": "unresolved",
                            "user_input": "man in the mirror back",
                            "name": "man in the mirror back"
                        }
                    })
            )

    def test_correction_album_to_song_candidates(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
          )

        assert_context_conversation_deterministic_features(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play album thriller'), 'music_play', {'album': 'thriller'}),
              create_expected_output('Boom, here you go'),
             (create_payload('no not this one'), 'correction', {}),
              create_expected_output('Do you want thriller the song, artist or album?'),
             (create_payload('song'), 'correction', {'corrected_field':'song'}),
             create_expected_output('Here\'s what I found for thriller: thriller by michael jackson, thriller by fall out boy and thriller by soundsense. Which one do you want?',
                                    intent='correction'),
             (create_payload('thriller by fall out boy'), 'correction', {'new_value':'thriller by fall out boy'}),
             create_expected_output('Boom, here you go', intent='music_play',
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
                                "user_input": "thriller",
                                "popularity": 0.37,
                                "spoken_name": "thriller by fall out boy",
                                "type": "music_track"
                            }
                        })
            )


    def test_correction_with_preformatted_and_normalization(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )
        m.register_uri(
            'POST',
            PROACTIVE_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_and_preformatted_queries(
            self.model_name,
            self.drm,
            None,
            (create_payload('Play album thriller'), 'music_play', {'album': 'thriller'}, False),
            create_expected_output('Boom, here you go'),
            (proactive_hints_input_dict, True),
            create_expected_output(''),
            (create_payload('no not this one'), 'correction', {}, False),
            create_expected_output('Do you want thriller the song, artist or album?'),
            (create_payload('song'), 'correction', {'corrected_field': 'song'}, False),
            create_expected_output(
                'Here\'s what I found for thriller: thriller by michael jackson, thriller by fall out boy and thriller by soundsense. Which one do you want?',
                intent='correction'),
            (create_payload('Thriller By Fall Out Boy'), 'correction', {'new_value': 'Thriller By Fall Out Boy'}, False),
            create_expected_output('Boom, here you go', intent='music_play',
                                   fields={
                                       "song": {
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
                                           "user_input": "thriller",
                                           "popularity": 0.37,
                                           "spoken_name": "thriller by fall out boy",
                                           "type": "music_track"
                                       }
                                   })
        )


    def test_correction_preformatted_normalize_playable(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
             'POST',
             MUSIC_SKILL_URL,
             text=play_hello_response
          )

        m.register_uri(
            'POST',
            PROACTIVE_SKILL_URL,
            text=play_hello_response
        )

        assert_deterministic_conversation_and_preformatted_queries(
             self.model_name,
             self.drm,
             None,
             (create_payload('Play Hello'), 'music_play', {'playable': 'hello'}, False),
              create_expected_output('Boom, here you go'),
             (proactive_hints_input_dict, True),
              create_expected_output(''),
             (create_payload('no not this one'), 'correction', {}, False),
              create_expected_output('Do you want hello the song, artist or album?'),
             (create_payload('song'), 'correction', {'corrected_field':'song'}, False),
              create_expected_output(
                'Here\'s what I found for hello: hello by adele, hello by j cole, hello by beyoncé, hello by joe and hello by eminem. Which one do you want?'),
             (create_payload('Hello By Adele'), 'correction', {'new_value': 'Hello By Adele'}, False),
              create_expected_output('Boom, here you go', intent='music_play',
                                   fields={
                                       "song": {
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
                                           "user_input": "hello",
                                           "popularity": 0.55,
                                           "spoken_name": "hello by adele",
                                           "type": "music_track",
                                           "aliased_field_id": "song",
                                           "casted": False,
                                           "resolve_type": "knowledge_resolution",
                                           "score": 0.55
                                       }
                                   })
            )
