from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase


class PersonType(EntityTypeBase):
    id = 'person'
    value_field = 'name'

    def get_candidates(self, text: str, **kwargs):
        if text in self.all_values():
            return [{
                'name': text,
                'value': text,
                'subject_pronoun': self.get_subject_pronoun(text),
                'object_pronoun': self.get_object_pronoun(text),
            }]
        else:
            return []

    def all_values(self):
        return ['my husband', 'my wife', 'my son', 'my daughter', 'my friend']

    def get_subject_pronoun(self, text):
        return {'my husband': 'he',
                'my wife': 'she',
                'my son': 'he',
                'my daughter': 'she',
                'my friend': 'they'}.get(text, 'they')

    def get_object_pronoun(self, text):
        return {'my husband': 'him',
                'my wife': 'her',
                'my son': 'him',
                'my daughter': 'her',
                'my friend': 'them'}.get(text, 'them')

register_entity_type(PersonType())