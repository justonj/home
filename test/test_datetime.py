import pytz
from datetime import datetime, timedelta, time

from nlu.knowledge_base.entity_type_registry import EntityType
from nlu.dialogue_system.dialogue_state import DialogueState
from nlu.dialogue_system.test_utils import create_payload


def get_date_entity(request, datetime_obj):
    return {
        'iso_time': '%s' % datetime_obj.date(),
        'type': 'date',
        'name': datetime_obj.strftime(r'%B %d')
    }


def get_time_entity(request, time_obj):
    return {
        'iso_time': '%s' % time_obj,
        'type': 'time',
        'name': time_obj.strftime(r'%-I:%M %p')
    }


def get_datetime_entity(request, datetime_obj):
    return {
        'iso_time': ('%s' % datetime_obj)[:-6],
        'type': 'datetime',
        'name': datetime_obj.strftime(r'%B %d at %-I:%M %p')
    }


class TestDatetimeEntities:
    model_name = 'aneeda_en'
    dialogue_state = None

    def setup_class(self):
        timezone = 'US/Pacific'
        self.dialogue_state = DialogueState('test', self.model_name)
        self.dialogue_state.payload = create_payload(tz=timezone)
        self.tz = pytz.timezone(timezone)

    def teardown_class(self):
        pass

    def now(self):
        return datetime.now(self.tz)

    def test_dates(self):
        inputs_outputs = [
            ('day after tomorrow', self.now() + timedelta(days=2)),
            ('day before yesterday', self.now() - timedelta(days=2)),
            ('today', self.now())
        ]

        entity_type = EntityType('date')

        for input_output in inputs_outputs:
            entities = entity_type.get_candidates(
                input_output[0],
                dialogue_state=self.dialogue_state)
        assert len(entities) == 1
        assert entities[0] == get_date_entity(input_output[0], input_output[1])

    def test_time(self):
        inputs_outputs = [
            ('7pm', time(19)),
            ('3am', time(3)),
            ('1300', time(13)),
            ('12', time(12)),
            ('14', time(14)),
            ('2310', time(23, 10)),
            ('9', time(9)),
            ('10', time(10)),
            ('1313', time(13, 13)),
            ('1', time(1))
        ]

        entity_type = EntityType('time')

        for input_output in inputs_outputs:
            entities = entity_type.get_candidates(
                input_output[0],
                dialogue_state=self.dialogue_state)
            assert len(entities) == 1
            assert entities[0] == get_time_entity(input_output[0], input_output[1])

    def test_unresolved_time(self):
        inputs = ['tomorrow']

        entity_type = EntityType('time')

        for input in inputs:
            entities = entity_type.get_candidates(
                input,
                dialogue_state=self.dialogue_state)
            assert len(entities) == 0

    def test_datetime(self):
        entity_type = EntityType('datetime')
        entities = entity_type.get_candidates(
            'tomorrow',
            dialogue_state=self.dialogue_state)
        assert len(entities) == 1
        expected_datetime = self.now() + timedelta(1)
        expected_datetime = expected_datetime.replace(hour=9, minute=0, second=0,
                                                      microsecond=0)
        assert entities[0] == get_datetime_entity('tomorrow', expected_datetime)

    def test_unresolved_datetime(self):
        inputs = ['xyz']

        entity_type = EntityType('datetime')
        for input in inputs:
            entities = entity_type.get_candidates(
                input,
                dialogue_state=self.dialogue_state)
            assert len(entities) == 0
