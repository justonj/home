import requests
import json
from nlu.knowledge_base.entity_type_base import EntityTypeBase
from nlu.payload_utils import get_user_identity_token
from nlu.knowledge_base.entity_type_registry import register_entity_type


class PhoneContactsType(EntityTypeBase):
    id = "user_phone_contact"

    def get_user_contacts(self, search_name, oauth_token):
        """Gets all the contacts from internal store. Identifies if there are multiple
        contacts or contacts with multiple numbers and creates candidates appropriately"""
        try:
            response = self.retrieve_contacts(search_name, oauth_token)
            contacts = response['contacts']
            matched_contacts = []
            for contact in contacts:
                contact_name = contact.get('contactName')
                contact_id = contact.get('id')
                contact_phone_numbers = contact.get('contactNumber')

                # If name is not proper or list is empty
                if (not contact_name or len(contact_phone_numbers) == 0):
                    print("Invalid contact. Ignoring it")
                    continue

                # Get all the contact numbers for this contact
                number_candidates = []
                for contact_number in contact_phone_numbers:
                    phone_number = contact_number.get('phoneNumber')
                    phone_type = contact_number.get('type')

                    # If phone number is empty, ignore this number
                    if not phone_number:
                        continue

                    number_candidates.append(
                        self.create_number_entity(contact_id, contact_name,
                                                  phone_number, phone_type))

                matched_contacts.append(self.create_contact_entity(
                    contact_id, contact_name, number_candidates))

            if (len(matched_contacts) == 1) and 'candidates' in matched_contacts[0]:
                matched_contacts = matched_contacts[0]['candidates']
            return matched_contacts

        except (IndexError, KeyError, TypeError, ValueError,
                json.decoder.JSONDecodeError) as e:
            print('Failed to retrieve user phone contacts:', e)
        return []

    def create_number_entity(self, id, name, phone_number, phone_type):
        """Creates a phone contact entity"""
        label_type = self.get_phone_type_label(phone_type)
        return {
            'spoken_name': label_type,
            'id': id,
            'name': name,
            'phone_number': phone_number,
            'phone_type': phone_type,
            'phone_type_label': label_type
        }

    def create_contact_entity(self, id, name, phone_numbers):
        """Creates a phone contact entity"""
        contact_entity = {
            'spoken_name': name,
            'id': id,
            'name': name
        }

        if len(phone_numbers) == 1:
            contact_entity['phone_number'] = phone_numbers[0]['phone_number']
            contact_entity['phone_type'] = phone_numbers[0]['phone_type']
            contact_entity['phone_type_label'] = phone_numbers[0]['phone_type_label']
        else:
            contact_entity['candidates'] = phone_numbers

        return contact_entity

    def get_phone_type_label(self, phone_type):
        """Returns the label for the phone number type"""
        return {
            1: 'home',
            2: 'mobile',
            3: 'work',
            4: 'faxWork',
            5: 'faxHome',
            6: 'pager',
            7: 'other',
            8: 'callback',
            9: 'car',
            10: 'companyMain',
            11: 'isdn',
            12: 'main',
            13: 'otherFax',
            14: 'radio',
            15: 'telex',
            16: 'ttytdd',
            17: 'workMobile',
            18: 'workPager',
            19: 'assistant',
            20: 'mms'
        }.get(phone_type, 'other')  # default to other if phone_type is not found

    def retrieve_contacts(self, search_name, oauth_token):
        """Retrieves all the contacts matching the search name from our
        internal store at a given URL"""
        url = 'http://api.sensiya.com/contacts'
        headers = {'Auth-Token': oauth_token}
        params = {'name': search_name}

        response = requests.get(url=url, params=params, headers=headers)
        print('response: ', response.text)
        return json.loads(response.text)

    def get_candidates(self, _text, **kwargs):
        """Gets the candidates for user's phone contacts. The candidates can
        be based on these conditions
        1. If exact match, then only one contact is returned
        2. If multiple contacts are returned, then all matching contacts are returned
        3. If contact has multiple phone numbers, then the contact name is duplicated with entry
           for each contact"""

        # Get the iam+ identity auth token. If its missing, return immediately
        dialogue_state = kwargs.get('dialogue_state')
        oauth_token = get_user_identity_token(dialogue_state)
        if oauth_token is None:
            print('user_phone_contact get_candidates ERROR: No auth token')
            return []

        # Check if the text is not empty or just containing spaces
        if (not _text or _text.isspace()):
            print('user_phone_contact get_candidates ERROR: input is empty')
            return []

        return self.get_user_contacts(_text, oauth_token)


register_entity_type(PhoneContactsType())
