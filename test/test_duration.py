from nlu.dialogue_system.dialogue_state import DialogueState
from nlu.knowledge_base.entity_type_registry import EntityType


class TestDurationEntities:
    model_name = 'blank_en'
    dialogue_state = None

    def setup_class(self):
        self.dialogue_state = DialogueState('test', self.model_name)

    def teardown_class(self):
        pass

    def test_short_durations(self):
        inputs_outputs = [
            ('three and a half hours', 210),
            ('three days and two and a quarter hours', (3*60*24 + 2 * 60 + 15)),
            ('three and half hours', 210),
            ('three and three quarters hours', 225),
            ('two days and twenty minutes', (2*60*24 + 20)),
            ('two days and 20 minutes', (2*60*24 + 20)),
            ('two days and 20 minutes', (2*60*24 + 20)),
            ('2 days and twenty minutes', (2*60*24 + 20)),
            ('three and a half weeks', (60*24*7*3 + int(60*24*7/2))),
            ('2 months and two weeks and 2 days', (60*24*30*2 + 60*24*7*2 + 60*24*2)),
        ]

        entity_type = EntityType('short_duration')

        for input_output in inputs_outputs:
            entities = entity_type.get_candidates(
                input_output[0],
                dialogue_state=self.dialogue_state)
            assert len(entities) == 1
            assert entities[0] == {
                'mins': input_output[1],
                'type': 'short_duration',
                'name': input_output[1]
            }
