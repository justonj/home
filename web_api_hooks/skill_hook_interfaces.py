import json
import requests

from py_zipkin.zipkin import create_http_headers_for_new_span

from config import config


def mention_value(mentions, field_id):
    for mention in mentions:
        if mention.field_id == field_id and mention.has_entity():
            return mention.entity
    return {}


def create_headers():
    headers = {'content-type': 'application/json'}
    headers.update(create_http_headers_for_new_span())
    return headers


def _retrieve(skill_url, **kwargs):
    _dialogue_state = kwargs.get('dialogue_state')
    url = skill_url + '/retrieve'
    data = {'nlu_response': _dialogue_state.to_json()}
    print('request body:', data)
    response = requests.post(url, json=data, headers=create_headers(),
                             timeout=config.SKILL_REQUEST_TIMEOUT)
    print('response: ', response.text)
    return json.loads(response.text)


if config.ENABLE_WEBHOOKS:
    pass