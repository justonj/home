import jsonapi_requests.data
from nlu_applications.ho.user_data_manager.user_data_manager import get_user_data_manager
import glob
import importlib.machinery
from config import config
import os

def validate_user_entity_json_api(payload):
    user_entities = jsonapi_requests.data.JsonApiResponse.from_data(payload)

    # If user_entities is not  generated || if we convert user_entities back to json format, if
    # it doesn't match the payload, then validation fails
    if user_entities is None or (user_entities.as_data() != payload):
        return False, 'Error in payload format'

    if not user_entities.data:
        return False, 'Error in payload: Data is not present'

    if not user_entities.included:
        return False, 'Error in payload: Included is not present'

    return True, 'OK'


def retrieve_relation_attributes(included, id, type):
    for item in included:
        if item['id'] == id and item['type'] == type:
            return item['attributes']


def retrieve_user_entities_from_jsonapi(payload):
    user_entities = jsonapi_requests.data.JsonApiResponse.from_data(payload)

    result_entities = []
    json_user_entities = user_entities.as_data()
    for user_entity in json_user_entities['data']:
        result_entity = {}
        type = user_entity['type']

        if 'attributes' not in user_entity:
            continue

        replace = user_entity['attributes']['replace'] if 'replace' in user_entity['attributes'] else True
        entries = user_entity['attributes']['entries'] if 'entries' in user_entity['attributes'] else []
        print('entries', entries)
        if not entries:
            continue

        relation = user_entity['relationships']
        key_count = len(relation.keys())
        retrieved_count = 0
        for key in relation.keys():
            data = relation[key]['data']
            print(key, '=', data)
            if 'id' not in data or 'type' not in data:
                print('id or type is missing for ', key)
                break

            relation_attributes = retrieve_relation_attributes(json_user_entities['included'], data['id'], data['type'])
            if relation_attributes is None:
                print('unable to get relation attributes for ', key)
                break

            result_entity[key] = relation_attributes
            retrieved_count += 1

        if retrieved_count != key_count:
            print('retrieved count = ', retrieved_count, 'for type=', type)
            continue

        result_entity['type'] = type
        result_entity['replace'] = replace
        result_entity['entries'] = entries
        result_entities.append(result_entity)

    return result_entities


def add_extracted_user_entities(data):
    for item in data:
        manager = get_user_data_manager(item['type'])
        if manager is None or not manager.add_user_specific_data(item):
            return False, item['type']

    return True, ''


def delete_extracted_user_entity(dataType, data):
    manager = get_user_data_manager(dataType)
    if manager is None or not manager.delete_user_specific_data(data):
        return False

    return True


# persists user specific data
def set_user_specific_entity(dataType, data):
    manager = get_user_data_manager(dataType)
    print(manager)
    if manager is None or not manager.persist_user_specific_data(data):
        return False

    return True


def load_user_data_managers():
    # Load all data managers
    for idx, filename in enumerate(
            glob.glob(os.path.join(config.APPLICATION_DIR, 'user_data_manager', 'managers', '*.py'))):
        print("Loading data managers from", filename)
        module_name = 'data_managers' + str(idx)
        loader = importlib.machinery.SourceFileLoader(module_name, filename)
        loader.load_module(module_name)