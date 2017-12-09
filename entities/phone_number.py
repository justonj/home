from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
import re
from faker import Factory

class PhoneNumberType(EntityTypeBase):
    id = 'phone_number'
    fake_factory = Factory.create()

    def get_candidates(self, text, **kwargs):
        phone_matcher = re.compile(r'^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$')
        phone_number = phone_matcher.search(text)
        if phone_number:
            phone_number = phone_number.group(0)
            return [
                {DEFAULT_VALUE_KEY: phone_number,
                 'type': self.id}
            ]
        else:
            return []

    def generate(self):
        while True:
            yield str(self.fake_factory.phone_number())


register_entity_type(PhoneNumberType())
