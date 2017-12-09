from typing import List

from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_retrieval_rule
from nlu.knowledge_base.entity_type_registry import EntityType
from nlu.knowledge_base.entity_resolution import resolve_entity
from nlu.mentions.mention_model_features import CRFFeatureExtractor
from nlu.tokenizer import tokenize, normalize


class CorrectSongArtistErrors(KnowledgeRetrievalRuleBase):
    intent_id = 'music_play'
    model_id = 'blank_en'
    fields_precondition = []  # type: List[str]
    rewrite_dialogue_state = True

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        # Detect if a track or artist was incorrectly extracted as an artist or
        # track, respectively
        for mention in dialogue_state.mentions:
            if (mention.type_name == 'music_track' and
                    not mention.has_entity() and
                    not mention.has_candidates()):
                if not any(mention.type_name == 'music_artist'
                           for mention in dialogue_state.mentions):
                    entity_type = EntityType('music_artist')
                    results, _, _ = resolve_entity(entity_type,
                                                mention.value,
                                                **kwargs)
                    if len(results) == 1:
                        new_dialogue_state = dialogue_state.clone()
                        new_dialogue_state.remove_mention(mention.field_id)
                        new_dialogue_state.create_and_add_mention('artist',
                                                                  entity=results[0])
                        return new_dialogue_state
            elif (mention.type_name == 'music_artist' and
                  not mention.has_entity() and
                  not mention.has_candidates()):
                if not any(mention.type_name == 'music_track'
                           for mention in dialogue_state.mentions):
                    entity_type = EntityType('music_track')
                    results, _, _ = resolve_entity(entity_type,
                                                mention.value,
                                                **kwargs)
                    if len(results) == 1:
                        new_dialogue_state = dialogue_state.clone()
                        new_dialogue_state.remove_mention(mention.field_id)
                        new_dialogue_state.create_and_add_mention('song',
                                                                  entity=results[0])
                        return new_dialogue_state
        return dialogue_state

# register_retrieval_rule(CorrectSongArtistErrors())


class MusicPlaySubstringMatchingInsteadOfMachineLearning(KnowledgeRetrievalRuleBase):
    intent_id = 'music_play'
    model_id = 'blank_en'
    fields_precondition = []  # type: List[str]
    result_fields = ['song', 'artist']
    extractor = CRFFeatureExtractor('en')

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        if dialogue_state.query is None or len(dialogue_state.mentions) > 0:
            return {}

        tokenized = tokenize(normalize(dialogue_state.query))
        features = [[] for _ in tokenized]
        results = self.extractor.add_knowledge_base_features(tokenized, features)
        artist_slice = [None, None]
        song_slice = [None, None]
        album_slice = [None, None]

        def set_slices(entity_type_name, slice_, idx, word_features):
            prefix = 'ent:%s:' % entity_type_name
            features = [x for x in word_features
                        if x.startswith(prefix)]
            if prefix + 'START' in features:
                slice_[0] = idx
            elif prefix + 'END' in features:
                slice_[1] = idx + 1
            elif prefix + 'STARTEND' in features:
                slice_[0] = idx
                slice_[1] = idx + 1

        def get_mention(entity_type_name, field_name, slice_):
            if None not in slice_:
                entity_name = ' '.join(tokenized[slice_[0]:slice_[1]])
                result, _, _ = resolve_entity(EntityType(entity_type_name),
                                           entity_name,
                                           **kwargs)
                print('result =', result[0] if result else result)
                if result:
                    return {field_name: result[0]}

        for idx, word_features in enumerate(results):
            set_slices('music_artist', artist_slice, idx, word_features)
            set_slices('music_track', song_slice, idx, word_features)
            set_slices('music_album', album_slice, idx, word_features)

        return get_mention('music_artist', 'artist', artist_slice) \
            or get_mention('music_track', 'song', song_slice) \
            or get_mention('music_album', 'album', album_slice) \
            or {}

# register_retrieval_rule(MusicPlaySubstringMatchingInsteadOfMachineLearning())
