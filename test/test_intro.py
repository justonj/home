import os

import json
import pytest
import requests_mock

from nlu.dialogue_system.test_utils import \
    assert_deterministic_conversation_features_with_options, \
    create_payload, create_expected_output, add_dialogue_rules_from_csv
from nlu.skills.skill_manager import get_skill
from .utils import read_response_file


MUSIC_SKILL_URL = get_skill('music').url + '/retrieve'

@pytest.mark.skip(reason="Intro intent is removed temporarily")
@requests_mock.Mocker(kw='mock')
class TestIntro(object):
    drm = None
    model_name = 'blank_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'intro.csv'),
            self.model_name,
            self.drm
        )
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'music.csv'),
            self.model_name,
            self.drm
        )

    def teardown_class(self):
        self.drm._clear_rules()

    def test(self, **kwargs):
        music_play_hello_json = read_response_file('music_play_hello.json')
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            status_code=200,
            text=music_play_hello_json
        )
        assert_deterministic_conversation_features_with_options(
            self.model_name,
            self.drm,
            (
                create_payload('nonempty query'),
                'intro',
                {'code': '7860c0c7d21f10c24b22d6b92521a933'}
            ),
            (
                True,
                create_expected_output(
                    "Hi I'm Aneeda. What music do you want to hear?",
                    fields={
                       "code": {
                            'name': '7860c0c7d21f10c24b22d6b92521a933',
                            'user_input': '7860c0c7d21f10c24b22d6b92521a933'
                        }
                    }
                ),
            ),
            (
                create_payload('hello by adele'),
                'music_play',
                {'song': 'hello',
                 'artist': 'adele'}
            ),
            (
                False,
                create_expected_output(
                    'Boom, here you go',
                    fields= {
                        "artist":{
                            'type': 'music_artist',
                            'id': '142111',
                            'popularity': 0.84,
                            'name': 'adele',
                            'user_input': 'adele'
                        },
                        "song":{
                            'type': 'music_track',
                            'user_input': 'hello',
                            'popularity': 0.55,
                            'spoken_name': 'hello by adele',
                            'id': '49422899',
                            'album': {
                                'id': '4872748',
                                'type': 'music_album',
                                'artist': {
                                    'id': '142111',
                                    'popularity': 0.84,
                                    'type': 'music_artist',
                                    'name': 'adele'
                                },
                                'name': 'hello'
                            },
                            'name': 'hello'
                        },
                        "tracks":{
                            'type': 'list',
                            'items': json.loads(music_play_hello_json)['fields']['tracks']['items']
                        }
                    }
                ),
            )
        )