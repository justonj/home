import pytest
from nlu.dialogue_system.test_utils import assert_intent, assert_annotation

from . import queries_transport as test_queries


class TestIntentClassification:

    def test_transport_taxi_book(self):
        for query in test_queries.taxi_book_queries:
            assert_intent(query,
                          expected_intent='transport_taxi_book',
                          expected_model='blank_en')

    def test_transport_duration_intent(self):
        for query in test_queries.taxi_duration_queries:
            assert_intent(query,
                          expected_intent='transport_taxi_estimate_travel_time',
                          expected_model='blank_en')

    def test_transport_fare_estimate_intent(self):
        for query in test_queries.taxi_fare_queries:
            assert_intent(query,
                          expected_intent='transport_taxi_estimate_travel_fare',
                          expected_model='blank_en')

    def test_transport_cancel_intent(self):
        for query in test_queries.taxi_cancel_queries:
            assert_intent(query,
                          expected_intent='transport_taxi_cancel',
                          expected_model='blank_en')

    def test_transport_current_status_intent(self):
        for query in test_queries.taxi_current_status_queries:
            assert_intent(query,
                          expected_intent='transport_taxi_current_status',
                          expected_model='blank_en')

    def test_transport_ride_history_intent(self):
        for query in test_queries.taxi_history_queries:
            assert_intent(query,
                          expected_intent='transport_taxi_ride_history',
                          expected_model='blank_en')


@pytest.mark.skip(reason="Transportation skill is disabled")
class TestEntityExtraction:

    def test_taxi_book_mentions_test(self):
        for i in range(len(test_queries.taxi_book_queries)):
            query = test_queries.taxi_book_queries[i]
            mentions = test_queries.taxi_book_mentions[i]
            assert_annotation(query, 'blank_en',
                              'transport_taxi_book', mentions)

    def test_taxi_duration_mentions_test(self):
        for i in range(len(test_queries.taxi_duration_queries)):
            query = test_queries.taxi_duration_queries[i]
            mentions = test_queries.taxi_duration_mentions[i]
            assert_annotation(query, 'blank_en',
                              'transport_taxi_estimate_travel_time', mentions)

    def test_taxi_fare_mentions_test(self):
        for i in range(len(test_queries.taxi_fare_queries)):
            query = test_queries.taxi_fare_queries[i]
            mentions = test_queries.taxi_fare_mentions[i]
            assert_annotation(query, 'blank_en',
                              'transport_taxi_estimate_travel_fare', mentions)

    def test_taxi_cancel_mentions_test(self):
        for i in range(len(test_queries.taxi_cancel_queries)):
            query = test_queries.taxi_cancel_queries[i]
            mentions = test_queries.taxi_cancel_mentions[i]
            assert_annotation(query, 'blank_en',
                              'transport_taxi_cancel', mentions)

    def test_taxi_status_mentions_test(self):
        for i in range(len(test_queries.taxi_current_status_queries)):
            query = test_queries.taxi_current_status_queries[i]
            mentions = test_queries.taxi_status_mentions[i]
            assert_annotation(query, 'blank_en',
                              'transport_taxi_current_status', mentions)
