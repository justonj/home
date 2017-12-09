from nlu.knowledge_base.knowledge_retrieval_manager import \
    KnowledgeRetrievalRuleBase, register_retrieval_rule
from nlu.knowledge_base.entity_type_registry import EntityType


class Condition:
    def __init__(self, type_name, mention_text):
        self.type_name = type_name
        self.mention_text = mention_text or None

    def matches(self, mention):
        return self.type_name == mention.type_name \
            and (self.mention_text in [None, mention.value])

    def __repr__(self):
        return '%s: %s' % (self.type_name, self.mention_text)


def collect_unique_matching_answer_entities(type_name, dialogue_states, conditions):
    """
    Return all unique answer mentions entities of the given type from the given
    dialogue_states that have mentions matching all given conditions.
    Example: if a condition "type_name = music_artist, look for dialogue states
    that have a mention of type music_artist. If you find such a dialogue state,
    look for all the answer fields and take those of type `type_name`.  Results
    are returned in the order of the dialogue_states. Uses entity field `id`
    to determine uniqueness.
    """
    entity_ids = set()
    result = []

    def add_entity(entity):
        id_ = (entity or {}).get('id')
        if id_ not in {None} | entity_ids:
            result.append(entity)
            entity_ids.add(id_)

    for dialogue_state in dialogue_states:
        mentions = dialogue_state.mentions
        if all(any(cond.matches(m) for m in mentions) for cond in conditions):
            for mention in mentions:
                schema = dialogue_state.schema
                if schema and schema.is_answer_field(mention.field_id):
                    if mention:
                        if mention.type_name == type_name:
                            add_entity(mention.entity)
                        elif mention.is_list:
                            if mention.base_type_names == type_name:
                                for entity in mention.entities_list():
                                    add_entity(entity)
                            else:
                                for entity in mention.entities_list():
                                    if entity.get('type') == type_name:
                                        add_entity(entity)
                    break
    return result


class MusicReplay(KnowledgeRetrievalRuleBase):
    intent_id = 'music_replay'
    model_id = 'aneeda_en'
    fields_precondition = []
    result_fields = ['tracks']

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        mentions_dict = {m.field_id: m for m in dialogue_state.mentions}
        conditions = []

        album_mention = mentions_dict.get('album')
        album_type = EntityType('music_album')
        album_triggers = set(album_type.context_resolution_triggers)
        if album_mention:
            album_name = None
            if album_mention.value not in album_triggers:
                album_name = album_mention.value
            conditions.append(Condition('music_album', album_name))

        artist_mention = mentions_dict.get('artist')
        artist_type = EntityType('music_artist')
        artist_triggers = set(artist_type.context_resolution_triggers)
        if artist_mention:
            artist_name = None
            if artist_mention.value not in artist_triggers:
                artist_name = artist_mention.value
            conditions.append(Condition('music_artist', artist_name))

        album_artist_mention = mentions_dict.get('artist_album')
        if album_artist_mention:
            album_artist_name = None
            if album_artist_mention.value not in album_triggers | artist_triggers:
                album_artist_name = album_artist_mention.value
            conditions.append(Condition('music_album', album_artist_name))
            conditions.append(Condition('music_artist', album_artist_name))

        collection_mention = mentions_dict.get('collection')
        if collection_mention:
            collection_type = EntityType('music_collection')
            collection_triggers = collection_type.context_resolution_triggers
            collection_name = None
            if collection_mention.value not in collection_triggers:
                collection_name = collection_mention.value
            conditions.append(Condition('music_collection', collection_name))

        time_range = mentions_dict.get('time_range')
        if time_range and time_range.entity:
            start_time = time_range.entity['start']
            end_time = time_range.entity['end']
        else:
            start_time = None
            end_time = None
        dialogue_states = kwargs.get('user').get_dialogue_states(
            completion=True,
            start_time=start_time,
            end_time=end_time
        )
        tracks = collect_unique_matching_answer_entities('music_track', dialogue_states, conditions)
        if tracks:
            return {'tracks': {'type': 'list', 'name':'', 'items': tracks,
                               'item_types': ['music_track']}}

        tracks = collect_unique_matching_answer_entities('music_track', dialogue_states, [])
        if tracks:
            return {'other_tracks':  {'type': 'list', 'name':'',
                                      'items': tracks,
                                      'item_types': ['music_track']}}


register_retrieval_rule(MusicReplay())
