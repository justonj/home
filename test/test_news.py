import requests_mock
import pytest
import json
import os

from nlu.dialogue_system.test_utils import assert_conversation_features, create_payload, \
    create_expected_output, add_dialogue_rules_from_csv, assert_conversation_deterministic, \
    assert_deterministic_conversation_features
from nlu.skills.skill_manager import get_skill


NEWS_SKILL_URL = get_skill('news').url + '/retrieve'

queries_response_for_npr = [
        (('Show me the news','news_search',{}), NEWS_SKILL_URL, 'news_npr.json', 'Getting the latest from NPR.'),
        (('what is the news with Trump','news_search',{'artist_or_topic': 'trump'}), NEWS_SKILL_URL, 'news_topic_search.json', 'Getting you the latest news about trump'),
        (('Show me the news','news_search',{}), NEWS_SKILL_URL, 'news_exceptions.json', 'Sorry. I cant find headline.')
    ]

def read_file(filename):
   return open(os.path.join(pytest.SAMPLE_DATA_PATH , "news", filename)).read()

@requests_mock.Mocker(kw='mock')
class TestIntents:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        # seed dialogues
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.TEST_RESPONSES_PATH, 'news.csv'),
            self.model_name,
            self.drm
        )

    def teardown_class(self):
        self.drm.clear_rules()

    def test_news_intent(self, **kwargs):
        m = kwargs['mock']

        for query, url, response_file, expected_output in queries_response_for_npr:
            m.register_uri('POST',
                url,
                text=read_file(response_file))

            print("query:", query, " response file:", response_file)

            assert_conversation_deterministic(
                self.model_name,
                self.drm,
                query,
                expected_output
            )
