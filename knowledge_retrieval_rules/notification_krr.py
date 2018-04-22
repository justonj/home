from typing import List

from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_retrieval_rule
from nlu.interfaces.client_interface import dialogue_state_from_input
from nlu.payload_utils import get_payload_schema_version


def getFormedDialogState(mention, schema_version):
    return dialogue_state_from_input(
        mention['entity']['intent'],
        mention['entity']['fields'],
        schema_version=schema_version
    )


def isFormedDialogState(mention):
    return 'field_id' in mention and \
           mention['field_id'] == 'notification' and \
           'entity' in mention and \
           'intent' in mention['entity'] and \
           'fields' in mention['entity']


class NotificationRule(KnowledgeRetrievalRuleBase):
    intent_id = 'proactive_notifications'
    model_id = 'home_en'
    fields_precondition = 'DIALOGUE_COMPLETE'
    result_fields = ['notification']
    rewrite_dialogue_state = True

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        mentions = dialogue_state.mentions
        proactive_dialog_state = dialogue_state

        # check the mentions to see if there's a valid dialogState contained in the 'notification' entity,
        # and if so set the dialogState to that
        for item in mentions:
            mention = item.to_dict()
            if isFormedDialogState(mention):
                proactive_dialog_state = getFormedDialogState(
                    mention,
                    schema_version=get_payload_schema_version(
                        dialogue_state.payload))

        return proactive_dialog_state


register_retrieval_rule(NotificationRule())
