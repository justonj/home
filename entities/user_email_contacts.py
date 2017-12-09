import re

import nlog as log
from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from nlu_applications.aneeda.web_api_hooks.utils import get_configured_accounts
from nlu_applications.aneeda.user_data_manager.managers.email_contacts_manager import EmailContactsManager
from nlu.payload_utils import get_payload_query

email_matcher = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class UserEmailContact(EntityTypeBase):
    id = 'user_email_contacts'

    def create(self, entity):
        return {
            'type': self.id,
            DEFAULT_VALUE_KEY: entity['name'],
            'entity': entity,
        }

    def get_candidates(self, text, column_name=None, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        email_manager = EmailContactsManager()

        # get user id
        user_id = kwargs['user'].user_id

        if not user_id:
            return []

        accounts = get_configured_accounts(user_id)
        if not accounts:
            return []

        mention = dialogue_state.get_mention('email_from_account')
        if mention:
            default_email_provider = mention.entity_value \
                if mention.has_entity() else mention.value
        else:
            default_email_provider = email_manager.get_default_email_provider(
                user_id)

        if not default_email_provider or default_email_provider.lower() == 'none':
            return []


        # check if the input text is email address
        is_valid_email = re.match(email_matcher, text)

        db_contacts = []

        db_contacts = email_manager.find_contacts(
            user_id, default_email_provider, text, is_valid_email)

        # if contacts not present in previous search, try to fetch from
        # microsfot account.
        if not db_contacts:
            for account in accounts:
                if account is default_email_provider:
                    continue
                db_contacts = email_manager.find_contacts(
                    user_id, account, text, is_valid_email)
                if db_contacts:
                    break

        candidates = []

        if not db_contacts:
            print('User_Email_Contacts: No contact found for ', text)
            if is_valid_email:
                candidates.append({
                    'type': self.id,
                    'spoken_name': text,
                    'email_address': text,
                    DEFAULT_VALUE_KEY: ''
                })

            return candidates

        for db_contact in db_contacts:
            email_address = db_contact['contacts'][0]['email']
            candidates.append({
                'type': self.id,
                'spoken_name': '%s <%s>' % (db_contact['name'], email_address),
                DEFAULT_VALUE_KEY: db_contact['name'],
                'id': db_contact['id'],
                'email_address': email_address
            })

        return candidates


register_entity_type(UserEmailContact())
