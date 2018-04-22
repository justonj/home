from typing import List

from nlu.knowledge_base.entity_type_registry import EntityType
from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_retrieval_rule
from nlu.payload_utils import get_payload_location
import nlu_applications.home.web_api_hooks.google as google


class GetLocationTime(KnowledgeRetrievalRuleBase):
    intent_id = 'clock_time'
    model_id = 'home_en'
    fields_precondition = []  # type: List[str]
    result_fields = ['time']

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')

        # Set a default location
        lat = None
        lon = None

        location = get_payload_location(dialogue_state)
        if location:
            lat, lon = location

        # getting the user-specified location if available
        clock_location = dialogue_state.get_mention('clock_location')
        if clock_location and clock_location.has_entity():
            lat = clock_location.entity.get('lat')
            lon = clock_location.entity.get('lon')

        time_obj = google.get_location_time(lat, lon)
        if time_obj is None:
            return False

        return {'time': EntityType('time').from_datetime(time_obj)}


register_retrieval_rule(GetLocationTime())
