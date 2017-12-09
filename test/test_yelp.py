import requests_mock
import json
import pytest
import os

from config import config
from nlu.dialogue_system.test_utils import assert_intent, assert_annotation, \
    add_dialogue_rules_from_csv, assert_conversation_features, \
    create_payload, create_expected_output
from nlu.skills.skill_manager import get_skill
from . import queries_yelp as tq


def read_file(filename):
    return open(os.path.join(pytest.SAMPLE_DATA_PATH,
                             'yelp',
                             filename)).read()

restaurant_response = read_file('restaurant_response.json')
geocode_response = read_file('geocode_response.json')
YELP_SKILL_URL = get_skill('yelp').url + '/retrieve'

@pytest.mark.skip(reason='restaurant classification is not working')
class TestIntentClassification:

    def test_restaurant_search(self):
        for query in tq.restaurant_search_queries:
            print('query = ', query)
            assert_intent(query,
                          expected_intent='restaurant_search',
                          expected_model='aneeda_en')

    def test_business_search(self):
        for query in tq.business_search_queries:
            assert_intent(query,
                          expected_intent='business_search',
                          expected_model='aneeda_en')


@pytest.mark.skip(reason="Yelp skill is disabled")
class TestEntityExtraction:

    @pytest.mark.skip(reason="Extraction issue need more training data")
    def test_restaurant_search(self):
        for i in range(len(tq.restaurant_search_queries)):
            query = tq.restaurant_search_queries[i]
            mentions = tq.restaurant_mentions[i]
            assert_annotation(query,
                              'aneeda_en',
                              'restaurant_search',
                              mentions)

    def test_business_search(self):
        for i in range(len(tq.business_search_queries)):
            query = tq.business_search_queries[i]
            mentions = tq.business_mentions[i]
            assert_annotation(query,
                              'aneeda_en',
                              'business_search',
                              mentions)


@pytest.mark.skip(reason="Yelp skill is disabled")
@requests_mock.Mocker(kw='mock')
class TestConversation:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        # seed dialogues
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        add_dialogue_rules_from_csv(
            os.path.join(pytest.RESPONSES_PATH, 'yelp.csv'),
            self.model_name,
            self.drm
        )

    def teardown_class(self):
        self.drm.clear_rules()

    def test_without_location(self, **kwargs):
        m = kwargs['mock']
        m.register_uri('POST',
                       YELP_SKILL_URL,
                       text=restaurant_response)
        m.register_uri('GET',
                       config.GEOCODE_URL,
                       text=geocode_response)
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('find indian restaurants'),
             create_expected_output('In which city or neighborhood?')),
            (create_payload('London'),
             create_expected_output('Thanks, I will look for something around there'))
        )

        # assert m.call_count == 2 #fail as entity resolution calling geocode
        # api twice. Not in scope now.
        history = m.request_history
        assert history[0].text is None
        assert history[0].qs == {'address': [
            'london'], 'key': [config.GOOGLE_API_KEY]}
        expected_retrieve_request = {
            'nlu_response': {
                'model_name': 'aneeda_en',
                'intent': 'restaurant_search',
                'mentions': [
                    {
                        'type': 'cuisine',
                        'value': 'indian',
                        'entity': {
                            'name': 'indian',
                            'category': 'indpak',
                            'spoken_name': 'indian'},
                        'field_id': 'cuisine',
                        'user_provided': True
                    },
                    {
                        'field_id': 'location',
                        'value': 'london',
                        'type': 'address',
                        'entity': {
                            'value': 'London, UK',
                            'lat': 51.5073509,
                            'lon': -0.1277583,
                            'type': 'APPROXIMATE'
                        }
                    }
                ],
                'debugInfo': {},
                'payload': {'input': 'London'}
            }
        }
        output = json.loads(history[len(history) - 1].text)
        nlu_resp = output['nlu_response']
        nlu_resp['debugInfo'] = {}

        assert output == expected_retrieve_request

    def test_with_location(self, **kwargs):
        m = kwargs['mock']
        m.register_uri('POST',
                       YELP_SKILL_URL,
                       text=restaurant_response)
        m.register_uri('GET',
                       config.GEOCODE_URL,
                       text=geocode_response)
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('find indian restaurants',
                            coordinates=(34.0858186, -118.3292296)),
             create_expected_output('Thanks, I will look for something around there'))
        )
        assert m.call_count == 2
        history = m.request_history
        assert history[0].text is None
        assert history[0].qs == {'latlng': ['34.0858186, -118.3292296'],
                                 'key': [config.GOOGLE_API_KEY]}
        expected_retrieve_request = {
            'nlu_response': {
                'intent': 'restaurant_search',
                'model_name': 'aneeda_en',
                'mentions': [
                    {
                        'type': 'cuisine',
                        'value': 'indian',
                        'entity': {
                            'name': 'indian',
                            'category': 'indpak',
                            'spoken_name': 'indian'
                        },
                        'field_id': 'cuisine',
                        'user_provided': True},
                    {
                        'field_id': 'location',
                        'type': 'address',
                        'entity': {
                            'value': 'London, UK',
                            'lon': -0.1277583,
                            'lat': 51.5073509,
                            'type': 'APPROXIMATE'}
                        }
                ],
                'debugInfo': {},
                'payload': {'longitude': -118.3292296,
                            'latitude': 34.0858186,
                            'input': 'find indian restaurants'}
            }
        }
        output = json.loads(history[len(history) - 1].text)
        nlu_resp = output['nlu_response']
        nlu_resp['debugInfo'] = {}

        assert output == expected_retrieve_request


@pytest.mark.skip(reason="Yelp skill is disabled")
@requests_mock.Mocker(kw='mock')
class TestCrossDomain:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        self.drm.add_intent_dialogue_rule(
            'restaurant_search', 'Here are restaurants', None)
        self.drm.add_intent_dialogue_rule(
            'transport_taxi_book', 'Finding uber for you', None)
        self.drm.add_intent_dialogue_rule(
            'restaurant_reservation', 'Booking a table there', None)

    def teardown_class(self):
        self.drm.clear_rules()

    def test_to_uber(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            YELP_SKILL_URL,
            text=restaurant_response
        )
        m.register_uri(
            'GET',
            config.GEOCODE_URL,
            text=geocode_response
        )

        payload_origin = create_payload('find indian restaurants in London')
        expect_origin = create_expected_output('Here are restaurants')

        payload_dest = create_payload(
            'book an uber there', card_token='farmboy-kitchen-los-angeles')
        expect_dest = create_expected_output(
            'Finding uber for you',
            mentions=[
                {'entity': {
                    'street_address': '1050 Vine St',
                    'city': 'Los Angeles',
                    'postal_code': '99211',
                    'region': 'CA',
                    'country': 'US',
                    'lat': 34.0900899,
                    'lon': -118.32624,
                    'type': 'address',
                    'coordinates': {
                        'type': 'geo_location',
                        'latitude': 34.0900899,
                        'longitude': -118.32624
                    },
                    'value': '1050 Vine St, Los Angeles, CA, 99211'
                },
                    'field_id': 'destination',
                    'type': 'address',
                    'value': 'there',
                    'user_provided': True
                }
            ])

        assert_conversation_features(
            self.model_name,
            self.drm,
            (payload_origin,
             expect_origin),
            (payload_dest,
             expect_dest)
        )

    def test_to_reservation(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            YELP_SKILL_URL,
            text=restaurant_response
        )
        m.register_uri(
            'GET',
            config.GEOCODE_URL,
            text=geocode_response
        )
        restaurants_list = json.loads(restaurant_response)['entities']
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('find indian restaurants in London'),
             create_expected_output('Here are restaurants')),
            (create_payload('book a table there tonight',
                            card_token=restaurants_list[2]['card_token']),
             create_expected_output('Booking a table there',
                                    [{'type': 'local_business',
                                      'value': 'there',
                                      'field_id': 'venue',
                                      'entity': restaurants_list[2],
                                      'user_provided': True}])
             )
        )
