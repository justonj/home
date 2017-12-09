from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_types import WebHookEntity, CountType


class UberPoolCountType(CountType):

    def __init__(self):
        super().__init__()
        self.id = 'pool_count'

    def is_valid(self, num):
        if num == 1 or num == 2:
            return True
        return False

register_entity_type(UberPoolCountType())

register_entity_type(WebHookEntity('transport_taxi_service_type',
                                   'get_taxi_types'))
