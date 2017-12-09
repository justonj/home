from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY


class NewsTopic(EntityTypeBase):
    id = 'news_topic'

    def get_candidates(self, text, **kwargs):
        return [
            {DEFAULT_VALUE_KEY: text,
             'type': self.id}
        ]


register_entity_type(NewsTopic())
