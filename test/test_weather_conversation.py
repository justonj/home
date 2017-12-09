import requests_mock
import pytest
import json
import os

from config import config
from freezegun import freeze_time
from nlu.dialogue_system.test_utils import assert_conversation_deterministic, \
 assert_deterministic_conversation_features, create_payload,\
 create_expected_output, add_dialogue_rules_from_csv
from nlu.skills.skill_manager import get_skill


weather_find_response = open(pytest.SAMPLE_DATA_PATH +
                             '/weather/test_weather_find.json').read()
weather_find_response_dict = json.loads(weather_find_response)


WEATHER_SKILL_URL = get_skill('weather').url + '/retrieve'
geocode_response = open(pytest.SAMPLE_DATA_PATH + '/weather/geocode_response.json').read()
expected_mentions = open(pytest.SAMPLE_DATA_PATH + '/weather/weather_find_expected_mentions.json').read()
expected_mentions_dict = json.loads(expected_mentions)

queries_responses = [
     (('what is the weather today in bangalore', 'weather_find', {'location': 'Bengaluru, Karnataka, India',
      'weather_date_range': 'today'}),
      WEATHER_SKILL_URL, 'weather_find.json', 'Checking weather'),
     (('what is the weather today in bangalore', 'weather_find', {'location': 'Bengaluru, Karnataka, India',
      'weather_date_range': 'today'}),
      WEATHER_SKILL_URL, 'skill_exception_101.json', 'Sorry, there\'s something wrong with the weather app. Try again later.'),
     (('what is the weather today in bangalore', 'weather_find', {'location': 'Bengaluru, Karnataka, India',
      'weather_date_range': 'today'}),
      WEATHER_SKILL_URL, 'skill_exception_102.json', 'Sorry, the request timed out. Try again later?'),
     (('what is the weather today in bangalore', 'weather_find', {'location': 'Bengaluru, Karnataka, India',
      'weather_date_range': 'today'}),
      WEATHER_SKILL_URL, 'skill_exception_103.json', 'I\'m sorry, I can\'t do that yet.'),
]


def read_file(filename):
    return open(os.path.join(pytest.SAMPLE_DATA_PATH, "weather", filename)).read()

@requests_mock.Mocker(kw='mock')
class TestConversation:
    drm = None
    model = 'blank_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model)
        self.drm = getattr(pytest.response_managers, self.model)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'weather.csv'),
            self.model,
            self.drm
        )

    def teardown_class(self):
        self.drm.clear_rules()

    def test_weather_find_intents(self, **kwargs):
        m = kwargs['mock']
        for query, url, response_file, expected_output in queries_responses:
            m.register_uri(
                'POST',
                WEATHER_SKILL_URL,
                text=read_file(response_file)
            )
            m.register_uri('GET',
                           config.GEOCODE_URL, text=geocode_response)

            assert_conversation_deterministic(
                self.model,
                self.drm,
                query,
                expected_output)

    @freeze_time("2017-06-08 09:00:00")
    def test_weather_find_response(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            WEATHER_SKILL_URL,
            text=weather_find_response
        )
        m.register_uri('GET',
                       config.GEOCODE_URL,
                       text=geocode_response)

        assert_deterministic_conversation_features(
            self.model,
            self.drm,
            None,
            (create_payload('what is the weather today in bangalore'), 'weather_find', {'location': 'Bengaluru, Karnataka, India',
             'weather_date_range': 'today'}),
            create_expected_output('Checking weather',
                                    fields={
                                        'location': expected_mentions_dict['location'],
                                        'weather_date_range': expected_mentions_dict['date_range']
                                    })
        )
