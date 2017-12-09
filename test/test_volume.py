import os
import json

import pytest

from nlu.dialogue_system.test_utils import create_payload, \
    create_expected_output, add_dialogue_rules_from_csv, \
    assert_deterministic_conversation_features_with_options

queries_response = [
    ((create_payload('Set the volume all the way up'), 'volume_control', {'volume_max': 'all the way', 'volume_up': 'up'}),
     'volume_up_max.json'),
    ((create_payload('Set the volume all the way down'), 'volume_control', {'volume_max': 'all the way', 'volume_down': 'down'}),
     'volume_up_min.json'),
    ((create_payload('Set the volume to maximum'), 'volume_control', {'volume_max': 'maximum'}),
     'volume_max.json'),
    ((create_payload('Set the volume to minimum'), 'volume_control', {'volume_min': 'minimum'}),
     'volume_min.json'),
    ((create_payload('Set the volume to 2'), 'volume_control', {'volume_level': '2'}),
      'volume_set_2.json'),
    ((create_payload('decrease the volume by 2'), 'volume_control', {'volume_incremental': '2', 'volume_down': 'decrease'}),
      'volume_decrease_by_2.json'),
    ((create_payload('increase the volume by 5'), 'volume_control', {'volume_incremental': '5', 'volume_up': 'increase'}),
      'volume_increase_by_5.json')
]


class TestIntents:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        # seed dialogues
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'volume.csv'),
            self.model_name,
            self.drm
        )

    def teardown_class(self):
        self.drm.clear_rules()

    def test_volume_intent(self, **kwargs):
        for query, expected_output in queries_response:

            expected_json = json.load(open(os.path.join(pytest.SAMPLE_DATA_PATH, "volume", expected_output), 'r'))

            print('Query: ', query)
            print('Mentions_expected: ', expected_json)

            assert_deterministic_conversation_features_with_options(
                self.model_name,
                self.drm,
                query,
                (True, create_expected_output('', fields=expected_json['fields']))
            )
