import pytest
from . import queries_sports as tq
from nlu.dialogue_system.test_utils import assert_intent, assert_annotation

@pytest.mark.skip(reason="Sports skill training file is disabled")
class TestIntentClassification:
    def test_standing(self):
        for query in tq.sports_standings_queries:
            assert_intent(query,
                          expected_intent='sports_team_standing',
                          expected_model='aneeda_en')

    def test_results(self):
        for query in tq.sports_results_queries:
            assert_intent(query,
                          expected_intent='sports_team_results',
                          expected_model='aneeda_en')

    def test_schedule(self):
        for query in tq.sports_league_schedule:
            assert_intent(query,
                          expected_intent='sports_team_schedule',
                          expected_model='aneeda_en')


@pytest.mark.skip(reason="Sports skill training file is disabled")
class TestEntityExtraction:
    def test_schedule_extraction(self):
        for i in range(len(tq.sports_league_schedule)):
            query = tq.sports_league_schedule[i]
            mention = tq.schedule_mentions[i]
            assert_annotation(query,
                              'aneeda_en',
                              'sports_team_schedule',
                              mention)

    def test_results_extraction(self):
        for i in range(len(tq.sports_results_queries)):
            query = tq.sports_results_queries[i]
            mention = tq.results_mentions[i]
            assert_annotation(query,
                              'aneeda_en',
                              'sports_team_results',
                              mention)

    def test_standing_extraction(self):
        for i in range(len(tq.sports_standings_queries)):
            query = tq.sports_standings_queries[i]
            mention = tq.stading_mentions[i]
            assert_annotation(query,
                              'aneeda_en',
                              'sports_team_standing',
                              mention)
