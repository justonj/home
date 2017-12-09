import json
import nlog as log
import requests


from py_zipkin.zipkin import create_http_headers_for_new_span
from config import config
from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_types import GenericDatabaseEntityType
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from .address import AddressType
from faker import Factory


def create_headers():
    headers = {'content-type': 'application/json'}
    headers.update(create_http_headers_for_new_span())
    return headers


class Custom_Location(AddressType):

    id = 'custom_location_type'

    def generate(self):
        while True:
            yield str(self.fake_factory.address())

    def get_candidates(self, text, **kwargs):
        from nlu.skills.skill_manager import get_skill
        log.info('text is::', text)
        if text in ['home', 'work']:
            url = get_skill('transport').url + '/places'
            data = {'iAmPlusId': kwargs['user'].user_id,
                    'placeId': text}

            response = requests.post(url, json=data, headers=create_headers(),
                             timeout=config.SKILL_REQUEST_TIMEOUT)
            response_json = json.loads(response.text)
            log.info('Requesting for places %s', response_json)
            if not 'address' in response_json:
                return []
            else:
                log.info('response for placeid::%s', response_json)
                text = response_json['address']

        return super().get_candidates(text, **kwargs)


register_entity_type(Custom_Location())
