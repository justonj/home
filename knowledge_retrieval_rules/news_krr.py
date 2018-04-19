import nlog as log
from nlu.knowledge_base.entity_resolution import resolve_entity
from nlu.knowledge_base.entity_type_registry import EntityType

from nlu.knowledge_base.knowledge_retrieval_base import \
    KnowledgeRetrievalRuleBase
from nlu.knowledge_base.knowledge_retrieval_manager import \
    register_retrieval_rule


class AddArtistKrr(KnowledgeRetrievalRuleBase):
    intent_id = 'news_search'
    model_id = 'ho_en'
    fields_precondition = ['artist_or_topic']  # type: List[str]
    rewrite_dialogue_state = True

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        # Detect if a track or artist was incorrectly extracted as an artist or
        # track, respectively
        topic_mention = dialogue_state.get_mention('artist_or_topic')
        entity_type = EntityType('music_artist')
        results, _, _ = resolve_entity(entity_type,
                                    [],
                                    topic_mention.entity_value or
                                    topic_mention.value,
                                    enable_context_resolution=False,
                                    **kwargs)
        if len(results) > 0:
            dialogue_state.create_and_add_mention('music_artist', entity=results[0])

        log.info('news_krr, %s', results)
        return dialogue_state

register_retrieval_rule(AddArtistKrr())
