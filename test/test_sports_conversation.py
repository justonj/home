import requests_mock
import pytest
import json
import os

from nlu.dialogue_system.test_utils import assert_conversation_features, \
    add_dialogue_rules_from_csv, create_payload, create_expected_output
from config import config
from nlu.skills.skill_manager import get_skill

team_standing_response = open(
    pytest.SAMPLE_DATA_PATH + "/sports/sports_team_standings.json").read()
team_standing_response_dict = json.loads(team_standing_response)

team_schedule_response = open(
    pytest.SAMPLE_DATA_PATH + "/sports/sports_team_schedule.json").read()
team_schedule_response_dict = json.loads(team_schedule_response)

sports_schedule_expected_mentions = open(pytest.SAMPLE_DATA_PATH + "/sports/sports_schedule_expected_mentions.json").read()

SPORT_SKILL_URL = get_skill('sports').url + '/retrieve'


@pytest.mark.skip(reason="Sports skill training file is disabled")
@requests_mock.Mocker(kw='mock')
class TestCrossDomain:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.RESPONSES_PATH, 'sports.csv'),
            self.model_name,
            self.drm
        )

    def teardown_class(self):
        self.drm.clear_rules()

    def test_sports_schedule_mentions(self, **kwargs):
        m = kwargs['mock']
        m.register_uri('POST',
                       SPORT_SKILL_URL,
                       text=team_schedule_response)

        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('what is the schedule for mlb'),
             create_expected_output('Showing the schedule'))
        )

        history = m.request_history
        assert json.loads(history[0].text)['nlu_response']['mentions'] == \
            json.loads(sports_schedule_expected_mentions)
