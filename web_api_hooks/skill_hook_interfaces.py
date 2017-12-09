import json
from datetime import datetime
import pytz
import requests

from py_zipkin.zipkin import create_http_headers_for_new_span
from nlu.profiling import zipkin_trace

from config import config
from nlu.dialogue_system.dialogue_state import DialogueState
from nlu.knowledge_base.api_hooks.web_interface_hooks import register_hook
from nlu.knowledge_base.entity_type_registry import EntityType
from nlu.knowledge_base.entity_utils import find_match, format_entity_response
from nlu.skills.skill_manager import get_skill
from .utils import get_configured_accounts
from nlu.payload_utils import get_payload_location, get_payload_user_name, \
    get_payload_user_phone, get_payload_timezone


#Hardcoding of name and number is only for demo purposes.
# Once we enable for qa deployment we need to remove these and related code
ARES_PHONE_NUMBER = '+15622536770'
ARES_NAME = 'Dimitar'

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


def _get_movie_showtimes_hook(**kwargs):
    _dialogue_state = kwargs.get('dialogue_state')
    url = 'https://iamplus-skills-movies.herokuapp.com/retrieve'
    data = {'nlu_response': _dialogue_state.to_json()}
    enclosed_keys = ['localBusiness']
    return _get_local_businesses(_dialogue_state, url, data, enclosed_keys, 'movie_listings')


@zipkin_trace
def _get_tv_listing_hook(**kwargs):
    _dialogue_state = kwargs.get('dialogue_state')
    url = get_skill('tv').url + '/retrieve'
    data = {'nlu_response': _dialogue_state.to_json()}
    response = requests.post(url, json=data, headers=create_headers(),
                             timeout=config.SKILL_REQUEST_TIMEOUT)

    try:
        print('response: ', response.text)
        if not response.text:
            return {}

        skill_data = json.loads(response.text)
        program_list = skill_data.get('programs') or []
        metadata = skill_data.get('metadata') or {}
        return {'tv_listing': program_list,
                'metadata': metadata}

    except (IndexError, KeyError, TypeError, json.decoder.JSONDecodeError) as e:
        print('Failed to retrieve team schedule:', e)
        return {}


# returns the matched entity
@zipkin_trace
def _entity_uber_types_hook(**kwargs):
    dialogue_state = kwargs.get('dialogue_state', {})
    url = get_skill('transport').url + '/services'
    mentions = dialogue_state.mentions
    origin = mention_value(mentions, 'origin')
    lat = None
    lon = None
    if origin:
        lat = origin.get('lat')
        lon = origin.get('lon')
        if lat and lon:
            lat = float(lat)
            lon = float(lon)
        else:
            lat = lon = origin.get('place_id')
    else:
        # payload location is needed in the case user gives uber_type in initial query
        # e.g., book uberx to lax airport. Here entity_resolution hits before
        # knowledge_retrieval rule add origin in mentions
        payload_location = get_payload_location(dialogue_state)
        if payload_location:
            lat = float(payload_location[0])
            lon = float(payload_location[1])

    if lat and lon:
        data = {'latitude': lat, 'longitude': lon,
                'iAmPlusId': kwargs['user'].user_id}
    else:
        print('ERROR: current lat, lon is not provided.')
        return []
    response = requests.post(url, json=data, headers=create_headers(),
                             timeout=config.SKILL_REQUEST_TIMEOUT)
    service_types = []
    try:
        print('response: ', response, response.text)
        response_json = json.loads(response.text)
        if 'speakOut' in response_json:
            return []
        service_types = response_json
    except (IndexError, KeyError, TypeError, json.decoder.JSONDecodeError) as e:
        print('Error: in taxi_type entity webhook', e)
        return []

    matched_types = find_match(service_types, kwargs.get('text'))
    if matched_types and len(matched_types) == 1:
        matched_types[0]['type'] = 'transport_taxi_service_type'
        return format_entity_response(matched_types)
    return service_types


def _transport_is_pool(**kwargs):
    _dialogue_state = kwargs.get('dialogue_state')
    mentions = [] if _dialogue_state is None else _dialogue_state.mentions
    uber_type = mention_value(mentions, 'taxi_service_id')
    if uber_type and 'name' in uber_type:
        taxi = uber_type.get('name').lower()
        print('transport_is_pool uber type: ', taxi)
        if taxi in ['uberpool', 'pool']:
            return {'is_pool': {'name': True}}
    return {'is_pool': {'name': False}}


def _get_origin(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    mention = mention_value(dialogue_state.mentions, 'origin')
    if mention and mention.has_entity():
        return {}

    location = get_payload_location(dialogue_state)
    if location:
        return {
            'origin': EntityType('custom_location_type').address_from_coordinates(location[0], location[1], id='custom_location_type')
        }
    return {}


def _get_location(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    mentions = dialogue_state.mentions
    mention = dialogue_state.get_mention('location')
    if mention and mention.has_entity():
        return {}

    location = get_payload_location(dialogue_state)
    if location:
        return {
            'location': EntityType('address').address_from_coordinates(location[0], location[1])
        }
    return {}


def _get_user_info(**kwargs):
    user = kwargs.get('user')
    dialogue_state = kwargs.get('dialogue_state')
    dialogue_state.create_and_add_mention('user_id', entity={
        'name': user.user_id,
        'type': 'text'

    })
    user_name =  ARES_NAME or get_payload_user_name(dialogue_state)
    user_phone_number = ARES_PHONE_NUMBER or get_payload_user_phone(
        dialogue_state)
    if user_name:
        dialogue_state.create_and_add_mention('user_name', entity={
            'name': user_name,
            'type': 'text'
        })

    if user_phone_number:
        dialogue_state.create_and_add_mention('user_phone_number', entity={
            'name': user_phone_number,
            'type': 'phone_number'
        })
    return dialogue_state


@zipkin_trace
def _start_restaurant_reservation(**kwargs):
    _dialogue_state = kwargs.get('dialogue_state')
    url = get_skill('ares').url + '/retrieve'
    print('dialogue_state:: ', _dialogue_state, 'ares url:: ', url)
    data = {'nlu_response': _dialogue_state.to_json()}
    response = requests.post(url, json=data, headers=create_headers(),
                             timeout=config.SKILL_REQUEST_TIMEOUT)
    try:
        success = (response.status_code == requests.codes.ok)
        return {'result': success}

    except (IndexError, KeyError, TypeError) as e:
        print('Failed to initiate Ares reservation:', e)
        return {'result': False}


def _check_user_account_configured(**kwargs):
    accounts = get_configured_accounts(kwargs['user'].user_id)

    if not accounts:
        return {
                'is_any_email_acc_configured': EntityType('yes_no').get_candidates('no', **kwargs)[0],
                'email_from_account': EntityType('skill_name').get_candidates("", **kwargs)
                }

    return {}


def _check_user_account_presence(**kwargs):
    accounts = get_configured_accounts(kwargs['user'].user_id)
    dialogue_state = kwargs.get('dialogue_state')
    from_account = mention_value(dialogue_state.mentions, 'email_from_account')
    filled_fields = {}
    if not accounts:
        filled_fields['email_error'] = EntityType('error').create(
            'You have not added any accounts yet.', 1001)
    elif from_account and from_account['name'] not in accounts:
        filled_fields['email_error'] = EntityType('error').create(
            'This Account is not configured.', 1005)

    return filled_fields


def _get_local_business_address(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    local_business = mention_value(dialogue_state.mentions, 'business')
    address = local_business['address']
    if address:
        return {'business_address': address}
    return {}


def _get_local_business_rating(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    local_business = mention_value(dialogue_state.mentions, 'business')
    rating = local_business.get('rating')
    if rating:
        return {'business_rating': rating}
    return {}


def _get_local_business_phone(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    local_business = mention_value(dialogue_state.mentions, 'business')
    phone = local_business.get('phone_number')
    if phone:
        return {'business_phone': phone}
    return {}


def _get_local_business_price(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    local_business = mention_value(dialogue_state.mentions, 'business')
    price = local_business.get('price_range')
    if price:
        return {'business_price': price}
    return {}


def _get_local_business_reviews(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    local_business = mention_value(dialogue_state.mentions, 'business')
    reviews = local_business.get('reviews') or {}
    print('reviews >>>>> :', reviews)
    if reviews:
        return {'business_reviews': reviews}
    return {}


def _get_local_business_hours(**kwargs):
    dialogue_state = kwargs.get('dialogue_state')
    local_business = mention_value(dialogue_state.mentions, 'business')
    hours = local_business.get('hours') or []
    print('hours >>>>> :', hours)

    def format_time(time_text):
        datetime_obj = datetime.strptime(time_text, '%H%M')
        return datetime.strftime(datetime_obj, '%-I:%M %p')

    if hours:
        hours_obj = hours[0]
        timezone = get_payload_timezone(dialogue_state)
        current_date = datetime.now(pytz.timezone(timezone)).date()
        filtered_hours = list(filter(
            (lambda item: item.get('day') is current_date.weekday()),
            hours_obj.get('hours') or []
        ))
        formatted_hours = list(map(
            (lambda item: item.get('hours'))
        ))
        output = {'value': ', '.join(formatted_hours),
                  'hours': hours_obj}
        if 'is_open_now' in hours_obj:
            output['open_now'] = hours_obj.get('is_open_now')
            return {'business_hours': {'entity': output}}
    return {}


if config.ENABLE_WEBHOOKS:
    register_hook('get_movie_showtimes', _get_movie_showtimes_hook)
    register_hook('get_tv_listing', _get_tv_listing_hook)
    register_hook('get_taxi_types', _entity_uber_types_hook)
    register_hook('get_current_origin', _get_origin)
    register_hook('get_current_location', _get_location)
    register_hook('transport_is_pool', _transport_is_pool)

    register_hook('ares_user_info', _get_user_info)
    register_hook('start_ares_reservation', _start_restaurant_reservation)

    register_hook('user_account_check', _check_user_account_presence)
    register_hook('user_accounts_config_check', _check_user_account_configured)
    register_hook('get_local_business_address', _get_local_business_address)
    register_hook('get_local_business_phone', _get_local_business_phone)
    register_hook('get_local_business_reviews', _get_local_business_reviews)
    register_hook('get_local_business_price', _get_local_business_price)
    register_hook('get_local_business_hours', _get_local_business_hours)
    register_hook('get_local_business_rating', _get_local_business_rating)
