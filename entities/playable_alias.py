from collections import defaultdict

from nlu.knowledge_base.core_entities import AliasType
from nlu.knowledge_base.entity_type_base import CONTEXT_NAMED_ENTITY_RESOLUTION
from nlu.knowledge_base.entity_type_registry import register_entity_type


class PlayableType(AliasType):
    id = 'playable_alias'
    popular_artist_threshold = 0.6

    def select(self, candidates, priority_order):
        def max_key(item):
            return item.get('score') or 0

        candidates_by_aliased_fields = defaultdict(lambda: [])
        for candidate in candidates:
            candidates_by_aliased_fields[candidate['aliased_field_id']]\
                .append(candidate)

        popular_artist = None
        for aliased_field_id in priority_order:
            field_candidates = candidates_by_aliased_fields[aliased_field_id]
            if aliased_field_id == 'artist' and field_candidates:
                popular_artist = max(field_candidates, key=max_key)
                popularity = popular_artist.get('score') or 0
                if popularity >= self.popular_artist_threshold:
                    return popular_artist
                continue
            if field_candidates:
                return self.max_score_entity(field_candidates)

        # case when popular_artist's popularity < 0.5 and there are no song
        # and album candidates
        if popular_artist:
            return popular_artist

    def disambiguate_candidates(self, candidates, **kwargs):
        named_entity_resolved_candidates = [
            entity
            for entity in candidates
            if entity['resolve_type'] == CONTEXT_NAMED_ENTITY_RESOLUTION
        ]
        priority_order = kwargs.get('priority_order') or \
                         ['artist', 'song', 'album']
        if named_entity_resolved_candidates:
            return self.select(named_entity_resolved_candidates, priority_order)

        return self.select(candidates, priority_order)

register_entity_type(PlayableType())