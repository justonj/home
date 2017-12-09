import pytest

from . import queries_weather as tq
from nlu.dialogue_system.test_utils import assert_intent, assert_annotation
from nlu.skills.skill_manager import get_skill

@pytest.mark.skip(reason=" Not testing classification for weather")
class TestIntentClassification:

    def test_weather_find_intent(self):
        for query in tq.weather_find_queries:
            print('Query', query)
            assert_intent(query,
                          expected_model='blank_en',
                          expected_intent='weather_find')

    def test_weather_set_alert_intent(self):
        for query in tq.weather_alert_queries:
            print('Query', query)
            assert_intent(query,
                          expected_intent='weather_set_alert',
                          expected_model='blank_en')

@pytest.mark.skip(reason=" Not testing extraction for weather")
class TestEntityExtraction:

    def test_weather_find_entity_extraction(self):
        for i in range(len(tq.weather_find_queries)):
            query = tq.weather_find_queries[i]
            mentions = tq.weather_find_mentions[i]
            assert_annotation(query, 'blank_en', 'weather_find', mentions)

    def test_weather_alert_entity_extraction(self):
        for i in range(len(tq.weather_alert_queries)):
            query = tq.weather_alert_queries[i]
            mentions = tq.weather_alert_mentions[i]
            assert_annotation(query, 'blank_en',
                              'weather_set_alert', mentions)
