from flask import request, jsonify
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

import nlu_applications.blank.user_data_manager.user_entity_helpers as user_entity_helpers
from nlu_applications.blank.user_data_manager.user_data_manager import get_user_data_manager

from nlu_server import app
from config import config

# Load all data managers
user_entity_helpers.load_user_data_managers()


@app.route('/user/entities', methods=['POST'])
# Removing this until API ACL is powered by a DB backend
# @require_app_key
def add_user_entities():
    # enforce request requirements
    if not request.is_json:
        raise UnsupportedMediaType('Content-Type: application/json required')
    payload = request.json

    if not payload:
        raise BadRequest('Payload is empty')

    is_valid, msg = user_entity_helpers.validate_user_entity_json_api(payload)
    if not is_valid:
        raise BadRequest(msg)

    result_entities = user_entity_helpers.retrieve_user_entities_from_jsonapi(payload)
    if not result_entities:
        raise BadRequest('Unable to retrieve entities properly')

    is_valid, entity_type = user_entity_helpers.add_extracted_user_entities(result_entities)
    if not is_valid:
        raise BadRequest('Unsupported type: ' + entity_type)

    return jsonify({})


@app.route('/user_set_preferences', methods=['POST'])
def add_user_preferences():
    # enforce request requirements
    if not request.is_json:
        raise UnsupportedMediaType('Content-Type: application/json required')
    payload = request.json

    if not payload:
        raise BadRequest('Payload is empty')

    if not payload.get('user_id'):
        raise BadRequest('\'user_id\' must be provided')

    manager = get_user_data_manager('user_preferences') # Hardcoded because this will be pulled out
    manager.add_user_specific_data(payload)

    return jsonify({})


@app.route('/user_get_preferences', methods=['POST'])
def get_user_preferences():
    # enforce request requirements
    if not request.is_json:
        raise UnsupportedMediaType('Content-Type: application/json required')
    payload = request.json

    if not payload:
        raise BadRequest('Payload is empty')

    if not payload.get('user_id'):
        raise BadRequest('\'user_id\' must be provided')

    manager = get_user_data_manager('user_preferences') # Hardcoded because this will be pulled out
    response = manager.get_json_for_user_id(payload['user_id'].lower())

    return jsonify(response)


@app.route('/user/entities', methods=['DELETE'])
# Removing this until API ACL is powered by a DB backend
# @require_app_key
def delete_user_entities():
    data = {}
    data['userId'] = request.args.get('userId')
    data['accountType'] = request.args.get('accountType')
    data['accountId'] = request.args.get('accountId')
    entity_type = request.args.get('entityType')

    # Raise a bad request if any of the params are missing
    if not data['userId']:
        raise BadRequest('User ID is not provided')

    if not data['accountType']:
        raise BadRequest('Account Type is not provided')

    if not data['accountId']:
        raise BadRequest('Account ID is not provided')

    if not entity_type:
        raise BadRequest('Entity Type is not provided')

    if not user_entity_helpers.delete_extracted_user_entity(entity_type, data):
        raise BadRequest('Unsupported type:' + entity_type)

    return jsonify({})


@app.route('/user/setentity', methods=['POST'])
def set_default_user_entity():
    data = {}
    data['userId'] = request.args.get('userId')
    data['entityKey'] = request.args.get('entityKey')
    data['entityValue'] = request.args.get('entityValue')
    entity_type = request.args.get('entityType')
    print(entity_type)

    # Raise a bad request if any of the params are missing
    if not data['userId']:
        raise BadRequest('User ID is not provided')

    if not entity_type:
        raise BadRequest('Entity Type is not provided')

    if not data['entityKey']:
        raise BadRequest('Entity key is not provided')

    if not data['entityValue']:
        raise BadRequest('Entity value is not provided')

    if not user_entity_helpers.set_user_specific_entity(entity_type, data):
        raise BadRequest('set default user entity failed')

    return jsonify({})


#TODO: Get this stuff out of here after passthrough APIs are manages on the wrapper
# This import should be removed when passthrough parts are pulled out
import io_tasks.http_requests

activity_urls = {
    'dev': 'https://service-activities-dev.herokuapp.com/activity',
    'qa': 'https://service-activities-qa.herokuapp.com/activity',
    'staging': 'https://service-activities-stg.herokuapp.com/activity',
    'prod': 'https://service-activities.herokuapp.com/activity'
}


@app.route('/activity_summary', methods=['POST'])
def activity_summary_passthrough_request():
    return activity_passthrough_request('summary')


@app.route('/activity', methods=['POST'])
def activity_passthrough_request(child_endpoint=None):
    if config.ENVIRONMENT in activity_urls:
        url = activity_urls[config.ENVIRONMENT]
    else:
        url = activity_urls['prod']

    args = request.args
    if child_endpoint is not None:
        url = url + '/' + child_endpoint
    elif 'id' in args:
        url = url + '/' + args['id']

    activity_request = io_tasks.http_requests.post_request.apply_async((url, request.json, args))

    success, activity_response = activity_request.get()
    if not success:
        raise BadRequest('external API error\n' + activity_response)

    return jsonify(activity_response)
