from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from nlu.knowledge_base.entity_type_registry import register_entity_type


class ErrorType(EntityTypeBase):
    id = 'error'

    def create(self, error_msg, error_code):
        return {
            DEFAULT_VALUE_KEY: error_msg,
            'error_msg': error_msg,
            'error_code': error_code
        }

register_entity_type(ErrorType())
