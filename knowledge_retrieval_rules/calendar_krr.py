import dateutil

from nlu.knowledge_base.entity_type_registry import EntityType
from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_retrieval_rule
from nlu.knowledge_base.entity_type_base import DEFAULT_VALUE_KEY


class CreateCalendarFromEvent(KnowledgeRetrievalRuleBase):
    intent_id = 'calendar_create_event'
    model_id = 'ho_en'
    fields_precondition = ['event']
    allow_overwrite = True
    result_fields = ['event_date', 'event_time',
                     'event_title', 'event_location']

    def run(self, **kwargs):
        fields = kwargs.get('fields')
        if fields['event'] is None or not fields['event'].has_entity():
            return {}

        event = fields['event'].entity
        print("CreateCalendarFromEvent: ", event)
        if event is None:
            return {}

        datetime_iso_str = event['datetime']
        if not datetime_iso_str:
            return {}

        datetime_object = dateutil.parser.parse(datetime_iso_str)
        response = {
            'event_date': EntityType('date').from_datetime(datetime_object),
            'event_time': EntityType('time').from_datetime(datetime_object),
            'event_title': {
                'id': 'event_title',
                'type': 'text',
                DEFAULT_VALUE_KEY: event.get(DEFAULT_VALUE_KEY)
            }
        }

        loc = event.get('location') or None
        if loc is not None:
            response['event_location'] = {'id': 'event_location',
                                          'type': 'text',
                                          DEFAULT_VALUE_KEY: loc}

        print("CreateCalendarFromEvent response:", response)
        return response

register_retrieval_rule(CreateCalendarFromEvent())
