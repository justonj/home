import pytest

from . import queries_reservation as tq
from nlu.dialogue_system.test_utils import assert_intent, assert_annotation


@pytest.mark.skip(reason='No training done for reservation skill')
class TestIntentClassification:
    def test_restaurant_reservation(self):
        for query in tq.reservation_queries:
            assert_intent(query,
                          expected_intent='restaurant_reservation',
                          expected_model='blank_en')


@pytest.mark.skip(reason='No training done for reservation skill')
class TestEntityExtraction:
    def test_restaurant_reservation(self):
        for i in range(len(tq.reservation_queries)):
            query = tq.reservation_queries[i]
            mentions = tq.reservation_mentions[i]
            assert_annotation(query, 'blank_en',
                              'restaurant_reservation', mentions)
