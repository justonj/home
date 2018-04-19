from nlu.dialogue_system.dialogue_state import DialogueState
from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_retrieval_rule


class ResolveResumePrompt(KnowledgeRetrievalRuleBase):
    intent_id = 'resume_prompt'
    model_id = 'ho_en'
    fields_precondition = ['resume_yn']
    rewrite_dialogue_state = True

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        mention = dialogue_state.get_mention('resume_yn')
        if (mention and
                mention.has_entity() and
                mention.value == 'yes'):
            return dialogue_state.previous_dialogue_state

        return DialogueState(intent_id='start_dialogue',
                             model_name=dialogue_state.model_name)

register_retrieval_rule(ResolveResumePrompt())
