from typing import List

from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_retrieval_rule

class FormatVolume(KnowledgeRetrievalRuleBase):
    intent_id = 'volume_control'
    model_id = 'home_en'
    fields_precondition = []  # type: List[str]
    result_fields = ['volume_control']
    maximum_syn = ['maximum', 'max', 'high', 'top']
    minimum_syn = ['minimum', 'min', 'low', 'bottom']
    volume_progress = 0
    volume_maximum = 10
    volume_minimum = 1
    volume_step = 1
    action_increase = 1
    action_decrease = 2
    action_set = 3

    def set_volume(self, ds):

        option = self.action_set
        value = None

        volume_max_mention = ds.get_mention('volume_max')
        volume_min_mention = ds.get_mention('volume_min')
        volume_level_mention = ds.get_mention('volume_level')
        volume_down_mention = ds.get_mention('volume_down')
        volume_up_mention = ds.get_mention('volume_up')
        volume_incremental_mention = ds.get_mention('volume_incremental')

        if volume_max_mention:
            value = (self.volume_minimum
                     if volume_down_mention
                     else self.volume_maximum)
        elif volume_min_mention:
            value = self.volume_minimum
        elif volume_level_mention:
            if not volume_level_mention.has_entity(): return None
            level = volume_level_mention.entity.get('name')
            value = (self.volume_maximum
                     if level in self.maximum_syn
                     else self.volume_minimum if level in self.minimum_syn
                     else level)
        elif volume_down_mention or volume_up_mention:
            option = (self.action_decrease
                      if volume_down_mention
                      else self.action_increase)
            value = (volume_incremental_mention.value
                     if volume_incremental_mention
                     else self.volume_step)

        if value is None:
            level = ""
        else:
            level = str(float(value))

        return {
            'option': option,
            'progress': self.volume_progress,
            'name': level,
            'type': 'volume_control'
        }

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        return {'volume_control': self.set_volume(dialogue_state)}


register_retrieval_rule(FormatVolume())
