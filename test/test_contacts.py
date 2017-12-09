import pytest
import nlu_applications.aneeda.user_data_manager.user_entity_helpers as helper
from . import input_contacts as inputs


class TestUserEmailContacts:
    def setup_class(self):
        helper.load_user_data_managers()

    def test_validate_user_contact_payload(self):
        is_valid, msg = helper.validate_user_entity_json_api(inputs.correct_user_contact_json)
        if not is_valid:
            pytest.fail(msg)

    def test_retrieve_entities_from_payload(self):
        result_entities = helper.retrieve_user_entities_from_jsonapi(inputs.correct_user_contact_json)
        assert result_entities == inputs.add_entities

    def test_add_contacts(self):
        is_valid, entity_type = helper.add_extracted_user_entities(inputs.add_entities)
        if not is_valid:
            pytest.fail("Failed for entity_type:" + entity_type)

    def test_remove_account(self):
        assert helper.delete_extracted_user_entity('user_email_contacts', inputs.delete_params_1)
        assert helper.delete_extracted_user_entity('user_email_contacts', inputs.delete_params_2)