from nlu.knowledge_base.entity_types import CountType
from nlu.knowledge_base.entity_type_registry import register_entity_type


class ReservationCountType(CountType):

    def __init__(self):
        super().__init__()
        self.id = 'reservation_count'

    def is_valid(self, num):
        if num > 0 and num < 20:
            return True
        return False

register_entity_type(ReservationCountType())
