from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from nlu.knowledge_base.entity_type_registry import register_entity_type


class CorrectionFieldType(EntityTypeBase):
    id = 'correction_field'

    def create(self, correction_field_value):
        print('correctionfieldtype create', correction_field_value)
        return {
            'type': self.id,
            DEFAULT_VALUE_KEY: correction_field_value,
        }

register_entity_type(CorrectionFieldType())
