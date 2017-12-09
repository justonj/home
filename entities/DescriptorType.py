from nlu.knowledge_base.entity_type_registry import EntityType, \
    register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
from nlu.utils import model_language, contains_sublist
from nlu.tokenizer import normalize, tokenize


class DescriptorType(EntityTypeBase):

    def __init__(self, id, descriptor_dict, max_words=4):
        super().__init__()
        self.id = id
        self.descriptor_dict = descriptor_dict
        self.MAX_WORDS_FOR_DESCRIPTOR_ANSWER = max_words

    def get_candidates(self, text, **kwargs):
        _dialogue_state = kwargs.get('dialogue_state')
        model_name = _dialogue_state.model_name
        language = model_language(model_name)
        tokenized = tokenize(normalize(text))
        if len(tokenized) > self.MAX_WORDS_FOR_DESCRIPTOR_ANSWER:
            return []
        if language in self.descriptor_dict:
            descriptor_words = self.descriptor_dict[language]
        else:
            raise NotImplementedError("Language not supported")

        descriptor_phrases = (tokenize(normalize(x)) for x in descriptor_words)
        descriptor_count = sum(
            1 for x in descriptor_phrases if contains_sublist(tokenized, x))
        if descriptor_count > 0:
            return [
                {DEFAULT_VALUE_KEY: 'yes',
                 'type': self.id}
            ]
        return [
            {DEFAULT_VALUE_KEY: 'no',
             'type': self.id}
        ]

is_latest_descriptors = {'en': ['last', 'latest', 'new', 'lastest',
                                'just received', 'newest', 'most recent',
                                'most current', 'recent',
                                'recently received']}
is_unread_descriptors = {'en': ['unread', 'not read', 'new', 'not opened',
                                'unopened', 'haven\'t read', 'did not read',
                                'didn\'t read', 'unseen', 'missed']}

is_upcoming_descriptors = {'en': ['upcoming', 'forthcoming', 'next', 'future']}

register_entity_type(DescriptorType('latest_yn', is_latest_descriptors))
register_entity_type(DescriptorType('unread_yn', is_unread_descriptors))
register_entity_type(DescriptorType('upcoming_yn', is_upcoming_descriptors))
