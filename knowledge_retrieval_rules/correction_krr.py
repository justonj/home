from typing import List

import nlog as log
from nlu.knowledge_base.entity_resolution import resolve_entity
from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_retrieval_rule
from nlu.knowledge_base.entity_type_base import ALIAS_RESOLUTION, DEFAULT_VALUE_KEY
from nlu.knowledge_base.entity_type_registry import EntityType
from nlu.knowledge_base.entity_type_manager import get_entity_list_values
from nlu.tokenizer import tokenize, normalize
from nlu.utils import get_list_field_description
from nlu.dialogue_system.dialogue_state import DialogueState


def get_correction_supported_fields(schema):
    return [field for field in schema.all_fields() if schema.is_correction_enabled(field.get('id'))]

def create_dialogue_state_from_previous(previous_state, new_query):
    return DialogueState(model_name=previous_state.model_name,
                        intent_id=previous_state.intent_id,
                        query=new_query,
                        format_version=previous_state.format_version,
                        mentions=previous_state.mentions)


class ApplyCorrection(KnowledgeRetrievalRuleBase):
    intent_id = 'correction'
    model_id = 'home_en'
    fields_precondition = ['new_value']
    rewrite_dialogue_state = True

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        new_value = dialogue_state.get_mention('new_value').value
        old_value = None
        candidate_value_mention = dialogue_state.get_mention('candidate_value')
        if candidate_value_mention:
            value_changed = dialogue_state.get_mention('value_changed')
            if value_changed:
                old_value = new_value
            new_value = candidate_value_mention.value

        user = kwargs.get('user')
        if not user:
            return dialogue_state

        corrected_mention = dialogue_state.get_mention('corrected_field')
        if corrected_mention:
            prev_intent_field = dialogue_state.get_mention('prev_intent')
            prev_intent = prev_intent_field.value

            if prev_intent is None:
                return dialogue_state

            previous_states = user.get_most_recent_dialogue_state_for_intent(prev_intent, 1)
        else:
            previous_states = user.get_most_recent_dialogue_states_excluding_query(
                1,
                excluded_query_pattern='__preformatted__'
            )
        if len(previous_states) == 0:
            print("Len of previous_states == 0")
            return dialogue_state
        previous_state = previous_states[0]
        if previous_state.intent_id != 'music_play':
            return dialogue_state

        def matches_candidate_in_previous_entity(new_value, candidates):
            new_value = normalize(new_value)
            for candidate in candidates:
                spoken_name = candidate.get('spoken_name')
                if spoken_name is None:
                    continue

                if new_value in spoken_name:
                    return [candidate]

            return []

        def delete_krr_derived_fields(previous_state):
            derived_fields = []
            for mention in previous_state.mentions:
                user_provided = mention.user_provided
                if not user_provided:
                    derived_fields.append(mention.field_id)

            for field in derived_fields:
                previous_state.remove_mention(field)
            return previous_state

        def get_first_user_provided_mention(previous_state):
            for prev_mention in previous_state.mentions:
                user_provided = prev_mention.user_provided
                if user_provided:
                    return prev_mention

        def delete_alias_derived_field(previous_state, mention):
            if (mention and
                    mention.is_alias() and
                    mention.has_entity()):
                aliased_field_id = mention.entity.get('aliased_field_id')
                if aliased_field_id:
                    previous_state.remove_mention(aliased_field_id)

        # Usecase 1: NC-52 -> Check if user is using the trigger words
        # Retrieve the value from old field
        prev_field_value = None
        prev_field_id = None
        prev_mention = get_first_user_provided_mention(previous_state)
        if prev_mention is not None:
            prev_field_value = prev_mention.value
            prev_field_id = prev_mention.field_id

        if prev_field_value is not None:
            delete_alias_derived_field(previous_state, prev_mention)
            tokenized_new_value = tokenize(normalize(new_value))
            previous_schema = previous_state.schema
            correction_supported_fields = get_correction_supported_fields(previous_schema) or []
            for field in correction_supported_fields:
                entity_type = EntityType(field['type'])
                if entity_type is None:
                    continue

                is_correction = entity_type.is_type_identifier(tokenized_new_value)
                log.info('Is correction for %s %s %s' % (field['type'],
                                                         is_correction,
                                                         tokenized_new_value))
                if is_correction:
                    candidates, _,_ = resolve_entity(
                        entity_type,
                        [],
                        prev_field_value,
                        enable_context_resolution=False,
                        **kwargs)
                    candidates = entity_type.prepare_candidates(candidates,
                                                                user,
                                                                previous_state.mentions)
                    if len(candidates) > 1:
                        dialogue_state.create_and_add_mention('corrected_field',
                                                              value=field['id'],
                                                              user_provided=False,
                                                              candidates=candidates)
                        return dialogue_state

                    previous_state.create_and_add_mention(field['id'],
                                                          value=prev_field_value,
                                                          user_provided=True,
                                                          candidates=candidates)
                    if field['id'] != prev_field_id:
                        previous_state.remove_mention(prev_field_id)

                    previous_state = delete_krr_derived_fields(previous_state)
                    new_dialogue_state = create_dialogue_state_from_previous(previous_state, new_value)
                    return new_dialogue_state

        # check if it matches any corrected field candidates
        if corrected_mention is not None and corrected_mention.has_candidates():
            log.info('corrected_field: %s', corrected_mention)
            candidates = matches_candidate_in_previous_entity(new_value,
                                                              corrected_mention.candidates)
            log.info('candidates: %s', candidates)
            if len(candidates) > 0:
                previous_state.create_and_add_mention(corrected_mention.value,
                                                      value=old_value if old_value else prev_field_value,
                                                      candidates=candidates,
                                                      user_provided=True)
                if prev_field_id != corrected_mention.value:
                    previous_state.remove_mention(prev_field_id)

                previous_state = delete_krr_derived_fields(previous_state)
                new_dialogue_state = create_dialogue_state_from_previous(previous_state, new_value)
                return new_dialogue_state

        # Get the user mentions from previous state. This is needed by next set of use cases
        user_mentions = []
        for mention in previous_state.mentions:
            if mention.user_provided:
                user_mentions.append(mention)

        # Usecase 2: NC-53 -> Check if he is changing the value in the same entity
        for mention in user_mentions:
            if mention.value != new_value:
                entity_type = EntityType(mention.type_name)
                if entity_type is None:
                    continue

                # usecase 3: NC-71 -> Check if its already present in the candidates list
                mention_value = new_value
                remove_candidates = True
                entity = None
                candidates = []
                if mention.has_candidates():
                    candidates = matches_candidate_in_previous_entity(new_value,
                                                                      mention.candidates)

                if len(candidates) == 0:
                    if mention.is_alias():
                        kwargs['dialogue_state'] = previous_state
                        kwargs['field_id'] = mention.field_id

                    candidates, _, _ = resolve_entity(entity_type,
                                                   [],
                                                   new_value,
                                                   enable_context_resolution=False,
                                                   **kwargs)
                    candidates = entity_type.prepare_candidates(candidates,
                                                                user,
                                                                previous_state.mentions)
                    if mention.is_alias():
                        if len(candidates) > 1:
                            entity = entity_type.disambiguate_candidates(
                                candidates,
                                priority_order=dialogue_state.schema.aliased_field_ids(
                                    mention.field_id),
                                resolve_type=ALIAS_RESOLUTION
                            )
                    mention_value = new_value
                    dialogue_state.create_and_add_mention('value_changed',
                                                          value="True",
                                                          user_provided=False,
                                                          candidates=[])
                else:
                    # remove candidates only if its for new value and didnt
                    # resolve from the candidates
                    mention_value = old_value if old_value else prev_field_value
                    remove_candidates = False

                if len(candidates) > 0:
                    if mention.has_entity():
                        del mention.entity
                    if remove_candidates and mention.has_candidates():
                        del mention.candidates
                    if len(candidates) > 1:
                        if entity:
                            mention.entity = entity
                        mention.candidates = candidates
                        mention.value = mention_value

                        if not mention.has_entity or not mention.is_alias():
                            dialogue_state.create_and_add_mention('corrected_field',
                                                                  value=mention.field_id,
                                                                  user_provided=False,
                                                                  candidates=candidates)
                            return dialogue_state
                    else:
                        mention.entity = candidates[0]
                        mention.value = mention_value

                    previous_state.add_mention(mention)
                    previous_state = delete_krr_derived_fields(previous_state)
                    new_dialogue_state = create_dialogue_state_from_previous(previous_state, new_value)
                    return new_dialogue_state

        # Use case 4: ND-1012-> None of the resolution worked.
        # If there is a single mention in previous state, then substitute
        # the previous mention value with this new value, even if its not resolved. The skill
        # may handle with just value. Use case : "music track entity resolution failure explained
        # in bug ND-1012
        if len(user_mentions) == 1:
            mention = user_mentions[0]
            mention.value = new_value
            if mention.has_entity():
                del mention.entity
            if mention.has_candidates():
                del mention.candidates
            previous_state.add_mention(mention)
            previous_state = delete_krr_derived_fields(previous_state)
            new_dialogue_state = create_dialogue_state_from_previous(previous_state, new_value)
            return new_dialogue_state

        return dialogue_state


class GetCorrectionFields(KnowledgeRetrievalRuleBase):
    intent_id = 'correction'
    model_id = 'home_en'
    fields_precondition = []  # type: List[str]
    result_fields = ['correction_fields']

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        user = kwargs.get('user')
        if not user:
            return dialogue_state
        previous_states = user.get_most_recent_dialogue_states_excluding_query(
            1,
            excluded_query_pattern='__preformatted__'
        )
        if len(previous_states) == 0:
            print("Len of previous_states == 0")
            return {}
        previous_state = previous_states[0]
        if previous_state.intent_id != 'music_play':
            return {}

        dialogue_state.create_and_add_mention('prev_intent',
                                              value=previous_state.intent_id)

        field_value = None
        for prev_mention in previous_state.mentions:
            user_provided = prev_mention.user_provided
            if user_provided:
                field_value = prev_mention.value
                break

        if field_value is not None:
            dialogue_state.create_and_add_mention('old_value',
                                                  value=field_value)

        correction_fields = []
        previous_schema = previous_state.schema
        correction_supported_fields = get_correction_supported_fields(previous_schema) or []
        for field in correction_supported_fields:
            correction_fields.append(EntityType('correction_field')
                                    .create(field['id']))

        dialogue_state.create_and_add_mention('correction_fields',
                                              entity={
                                                  DEFAULT_VALUE_KEY: get_list_field_description(get_entity_list_values(correction_fields)),
                                                  'items': correction_fields}
                                              )

        return {}


class ApplyCorrectionFromDialog(KnowledgeRetrievalRuleBase):
    intent_id = 'correction'
    model_id = 'home_en'
    fields_precondition = ['corrected_field', 'correction_fields']
    rewrite_dialogue_state = True

    def delete_krr_derived_fields(self, previous_state):
        derived_fields = []
        for mention in previous_state.mentions:
            user_provided = mention.user_provided
            if not user_provided:
                derived_fields.append(mention.field_id)

        for field in derived_fields:
            previous_state.remove_mention(field)
        return previous_state

    def get_first_user_provided_mention(self, previous_state):
        for prev_mention in previous_state.mentions:
            user_provided = prev_mention.user_provided
            if user_provided:
                return prev_mention

    def get_candidate_matches(self, value, candidates):
        ret_candidates = []
        for candidate in candidates:
            spoken_name = candidate.get('spoken_name')
            if spoken_name is None:
                continue
            if value in spoken_name:
                ret_candidates.append(candidate)
        return ret_candidates

    def get_alias_entity(self, alias_mention, corrected_field_value, value):
        if alias_mention.has_entity():
            value = normalize(value)
            aliased_field_id = alias_mention.entity.get('aliased_field_id')
            spoken_name = alias_mention.entity.get('spoken_name')
            if (aliased_field_id and
                    aliased_field_id == corrected_field_value and
                    spoken_name and value in spoken_name):
                return alias_mention.entity

    def get_alias_candidates(self, alias_mention, corrected_field_value, value):
        candidates = []
        if alias_mention.has_candidates():
            value = normalize(value)
            for candidate in alias_mention.candidates:
                log.info('candidate: %s', candidate)
                aliased_field_id = candidate.get('aliased_field_id')
                log.info('aliased_field_id: %s, corrected_filed : %s',
                         aliased_field_id, corrected_field_value)
                spoken_name = candidate.get('spoken_name')
                if (aliased_field_id is not None and
                        aliased_field_id == corrected_field_value and
                        spoken_name and value in spoken_name):
                    candidates.append(candidate)
        return candidates

    def get_resolved_candidates(self, previous_state, prev_field_value,
                                corrected_field_value, **kwargs):
        user = kwargs.get('user')
        correction_supported_fields = get_correction_supported_fields(previous_state.schema) or []
        correction_supported_field_ids = [field.get('id') for field in correction_supported_fields]
        if corrected_field_value not in correction_supported_field_ids:
            return True, []
        entity_type = EntityType(previous_state.schema.field_type(corrected_field_value))
        if entity_type is None:
            return True, []

        candidates, _, _ = resolve_entity(entity_type,
                                       [],
                                       prev_field_value,
                                       enable_context_resolution=False,
                                       **kwargs)
        candidates = entity_type.prepare_candidates(candidates, user,
                                                    previous_state.mentions)
        return False, candidates

    def get_candidates_for_alias_mention(self, prev_mention, corrected_field_value, value):
        candidates = self.get_alias_candidates(prev_mention, corrected_field_value, value)
        log.info('candidates: %s', candidates)
        if len(candidates) == 0:
            entity = self.get_alias_entity(prev_mention, corrected_field_value, value)
            log.info('entity: %s', entity)
            if entity:
                candidates = [entity]

        return candidates

    def get_candidates_for_existing_field(self, previous_state,
                                          corrected_field_value,
                                          value):
        value = normalize(value)
        mention = previous_state.get_mention(corrected_field_value)
        candidates = mention.candidates or []
        if len(candidates) == 0:
            entity = mention.entity
            if entity:
                spoken_name = entity.get('spoken_name')
                if spoken_name and value in spoken_name:
                    candidates.append(entity)
        return candidates

    def delete_alias_derived_field(self, previous_state, mention):
            if (mention and
                    mention.is_alias() and
                    mention.has_entity()):
                aliased_field_id = mention.entity.get('aliased_field_id')
                if aliased_field_id:
                    previous_state.remove_mention(aliased_field_id)

    def run(self, **kwargs):
        log.info('ApplyCorrectionFromDialog : rule start')
        dialogue_state = kwargs.get('dialogue_state')
        corrected_mention = dialogue_state.get_mention('corrected_field')
        corrected_field_value = corrected_mention.value

        log.info('corrected_field_value %s', corrected_field_value)

        prev_intent_field = dialogue_state.get_mention('prev_intent')
        prev_intent = prev_intent_field.value
        if prev_intent is None or prev_intent != 'music_play':
            return dialogue_state

        user = kwargs.get('user')
        log.info('user: %s', user)
        if not user:
            return dialogue_state
        previous_states = user.get_most_recent_dialogue_state_for_intent(prev_intent, 1)
        if len(previous_states) == 0:
            print("Len of previous_states == 0")
            return dialogue_state
        previous_state = previous_states[0]

        prev_mention = self.get_first_user_provided_mention(previous_state)

        log.info('prev mention %s', prev_mention)
        candidates = []
        if prev_mention is not None:
            prev_field_value = prev_mention.value
            prev_field_id = prev_mention.field_id

            self.delete_alias_derived_field(previous_state, prev_mention)

            resolve_candidates = False
            if prev_mention.is_alias():
                candidates = self.get_candidates_for_alias_mention(prev_mention,
                                                                   corrected_field_value,
                                                                   prev_field_value)
            elif prev_field_value is not None:
                if prev_field_id != corrected_field_value:
                    resolve_candidates = True
                else:  # if its same type no need to resolve but just get it from prev intent fields
                    candidates = self.get_candidates_for_existing_field(previous_state,
                                                                        corrected_field_value,
                                                                        prev_field_value)

            if len(candidates) == 0:
                resolve_candidates = True

            # no candidates for the corrected field from prev mention, resolve it
            if resolve_candidates:
                error, candidates = self.get_resolved_candidates(previous_state,
                                                                 prev_field_value,
                                                                 corrected_field_value,
                                                                 **kwargs)
                if error:
                    dialogue_state.remove_mention('corrected_field')
                    return dialogue_state

            if len(candidates) > 1:
                dialogue_state.create_and_add_mention('corrected_field',
                                                      value=corrected_field_value,
                                                      user_provided=False,
                                                      candidates=candidates)
            else:
                if prev_field_id != corrected_field_value:
                    previous_state.create_and_add_mention(
                        corrected_field_value,
                        value=prev_field_value,
                        user_provided=True,
                        candidates=candidates)
                    previous_state.remove_mention(prev_field_id)
                    previous_state = self.delete_krr_derived_fields(previous_state)
                return previous_state

        return dialogue_state


register_retrieval_rule(GetCorrectionFields())
register_retrieval_rule(ApplyCorrection())
register_retrieval_rule(ApplyCorrectionFromDialog())
