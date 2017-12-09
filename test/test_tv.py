from . import queries_tv as tq
from nlu.dialogue_system.test_utils import assert_intent, assert_annotation
import pytest
from nlu.skills.skill_manager import get_skill

@pytest.mark.skip(reason="TV skill training file is disabled")
class TestIntentClassification:
    def test_tv_listings(self):
        for query in tq.listings_queries:
            assert_intent(query,
                          expected_intent='tv_listings',
                          expected_model='blank_en')

    def test_tv_show_cast(self):
        for query in tq.show_cast_queries:
            assert_intent(query,
                          expected_intent='tv_show_cast',
                          expected_model='blank_en')

    def test_tv_show_description(self):
        for query in tq.show_description_queries:
            assert_intent(query,
                          expected_intent='tv_show_description',
                          expected_model='blank_en')

    def test_tv_show_episode_summary(self):
            for query in tq.show_episode_summary_queries:
                assert_intent(query,
                              expected_intent='tv_show_episode_summary',
                              expected_model='blank_en')


@pytest.mark.skip(reason="TV skill training file is disabled")
class TestEntityExtraction:
    def test_tv_listings(self):
        for i in range(len(tq.listings_queries)):
            query = tq.listings_queries[i]
            mentions = tq.listings_mentions[i]
            assert_annotation(query, 'blank_en',
                              'tv_listings', mentions)

    def test_tv_show_cast(self):
        for i in range(len(tq.show_cast_queries)):
            query = tq.show_cast_queries[i]
            mentions = tq.show_cast_mentions[i]
            assert_annotation(query, 'blank_en',
                              'tv_show_cast', mentions)

    def test_tv_show_description(self):
        for i in range(len(tq.show_description_queries)):
            query = tq.show_description_queries[i]
            mentions = tq.show_description_mentions[i]
            assert_annotation(query, 'blank_en',
                              'tv_show_description', mentions)

    def test_tv_show_episode_summary(self):
        for i in range(len(tq.show_episode_summary_queries)):
            query = tq.show_episode_summary_queries[i]
            mentions = tq.show_episode_summary_mentions[i]
            assert_annotation(query, 'blank_en',
                              'tv_show_episode_summary', mentions)

