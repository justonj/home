from nlu.knowledge_base.knowledge_retrieval_manager import KnowledgeRetrievalRuleBase, \
    register_generic_retrieval_rule
from nlu.knowledge_base.knowledge_retrieval_base import GenericRule

import nlu.knowledge_base.knowledge_base_helpers as helpers
from nlu.dialogue_system.dialogue_state import DialogueState

from nlu.knowledge_base.entity_type_registry import EntityType

import os
from config import config


class PermissionCheck(GenericRule):
    model_id = 'home_en'
    rewrite_dialogue_state = True
    result_fields = []


    def add_permissions(self, service, permission):
        return [{'service' : service, 'permission' : permission, 'value' : permission}]        

    def create_dlg_for_permission(self, dlg, permission_type, permission_status):
        new_dialogue_state = DialogueState(intent_id='permission_request',
                    model_name=dlg.model_name)
        new_dialogue_state.payload = dlg.payload
        new_dialogue_state.create_and_add_mention('permission', candidates=self.add_permissions(permission_type, permission_status))
        return  new_dialogue_state

    def run(self, **kwargs):
        dialogue_state = kwargs.get('dialogue_state')


        if 'permissions' in dialogue_state.payload:            
            user_permissions = dialogue_state.payload['permissions']
        else:
            return dialogue_state

        entity_type = EntityType('permission_request')
        list_permissions = entity_type.get_candidates(dialogue_state.intent_id, **kwargs)

        if list_permissions == [] or list_permissions[0]['permissions'] is None:
            return dialogue_state

        permissions_required = list_permissions[0]['permissions'].split()

        if permissions_required is None:
            return dialogue_state

        for permission in permissions_required:
            for user_permission in user_permissions:
                perm_service = user_permission['service'].lower()
                perm_status = user_permission['status'].lower()
                if  perm_service == permission and  perm_status in ['unknown', 'disabled']:
                        return self.create_dlg_for_permission(dialogue_state, permission, perm_status)

        return dialogue_state


#register_generic_retrieval_rule(PermissionCheck())
