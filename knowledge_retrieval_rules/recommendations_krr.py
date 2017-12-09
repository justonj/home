import os
import random
import re

from nlu.knowledge_base.knowledge_retrieval_base import KnowledgeRetrievalRuleBase
from nlu.knowledge_base.knowledge_retrieval_manager import register_retrieval_rule
from nlu.knowledge_base.entity_type_base import DEFAULT_VALUE_KEY
from nlu.knowledge_base.entity_relationships import TypeRelationshipManager
from config import config


SET_TYPES_ALLOWED = set(['music_track', 'music_album', 'music_artist'])
TEMPLATES_PATH = os.path.join(config.RAW_KNOWLEDGE_DIR, 'speakout_templates', 'recommendations.template')
TEMPLATES = []
replace_pattern = re.compile('<X>', re.IGNORECASE)

def is_music_recommendation(entity_item_types):
    set_entity_item_types = set(entity_item_types)
    return set_entity_item_types.issubset(SET_TYPES_ALLOWED)

def contains_music(entity_item_types):
    set_entity_item_types = set(entity_item_types)
    return not SET_TYPES_ALLOWED.isdisjoint(set_entity_item_types)

def is_music_list(item):
    item_type = item.get('type')
    list_item_types = item.get('item_types')
    if TypeRelationshipManager.is_list_type(item_type) and \
        is_music_recommendation(list_item_types):
        return True
    return False

def prepare_templates():
    if TEMPLATES:
        return

    fb = open(TEMPLATES_PATH)
    for line in fb:
        TEMPLATES.append(line.rstrip())

def get_random_speakout(name):
    if not name:
        return ''

    random_template = random.choice(TEMPLATES)
    return replace_pattern.sub(name, random_template)


class RecommendationsRule(KnowledgeRetrievalRuleBase):
    intent_id = 'proactive_recommendations'
    model_id = 'blank_en'
    fields_precondition = 'DIALOGUE_COMPLETE'
    rewrite_dialogue_state = True

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')
        mentions = dialogue_state.mentions
        for mention in mentions:
            if mention.field_id == 'recommendations':
                if  mention.has_entity() and \
                    mention.type_name == 'list' and \
                    'items' in mention.entity and \
                    contains_music(mention.base_type_names):

                    entity = mention.entity
                    for item in entity['items']:
                        if not is_music_list(item):
                            continue

                        prepare_templates()
                        item['speakout'] = get_random_speakout(item.get(DEFAULT_VALUE_KEY))
                else:
                    break
        return dialogue_state


register_retrieval_rule(RecommendationsRule())
