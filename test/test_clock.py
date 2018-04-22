import os

import pytest
import requests_mock
from freezegun import freeze_time

from nlu.dialogue_system.test_utils import add_dialogue_rules_from_csv, \
    assert_conversation_deterministic


def read_file(filename):
    return open(os.path.join(pytest.SAMPLE_DATA_PATH,
                             'clock',
                             filename)).read()

geocode_response = read_file('geo_location.json')
tz_la_response = read_file('tz_la.json')
tz_london_response = read_file('tz_london.json')

queries_response = [
    (('What time is it', 'clock_time', {}), tz_la_response, 'It is 12:00 PM'),
    (('what time is it in London', 'clock_time', {
        'clock_location': 'london'}), tz_london_response, 'It is 7:00 PM')
]

GOOGLE_API = 'https://maps.googleapis.com/maps/api/'
TIMEZONE_API = GOOGLE_API + 'timezone/json'
GEOCODE_API = GOOGLE_API + 'geocode/json'


@requests_mock.Mocker(kw='mock')
class TestIntents:
    drm = None
    model_name = 'home_en'

    def setup_class(self):
        # seed dialogues
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'clock_time.csv'),
            self.model_name,
            self.drm
        )

    def teardown_class(self):
        self.drm.clear_rules()

    @freeze_time("2017-06-01 19:00:00")
    def test_clock_intent(self, **kwargs):
        m = kwargs['mock']

        for query, tz, expected_output in queries_response:
            print('Query: ', query)
            print('tz: ', tz)
            print('expected: ', expected_output)

            m.register_uri('GET', TIMEZONE_API, text=tz)
            m.register_uri('GET', GEOCODE_API, text=geocode_response)

            assert_conversation_deterministic(
                self.model_name,
                self.drm,
                query,
                expected_output
            )
