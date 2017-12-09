import nlog as log
import nlu.knowledge_base.knowledge_base_helpers as helpers

from nlu.knowledge_base.entity_type_base import DEFAULT_VALUE_KEY
from nlu.knowledge_base.entity_types import GenericDatabaseEntityType
from nlu.knowledge_base.entity_type_registry import register_entity_type


class ServiceEntityType(GenericDatabaseEntityType):

    def get_candidates(self, text, **kwargs):
        result = super().get_candidates(text, **kwargs)
        if not result:
            result = helpers.retrieve_all_values(
                self.table_name,
                self.key_column_name,
                self.entity_response_columns,
                entity_type=self.id
            )

        if result and len(result) > 1:
            result = [item for item in result
             if item['account_type'] == 'email']

            log.info('supported emailaccounts: %s', result)

        for item in result:
            del item['account_type']

        return result


# register all intents in here
register_entity_type(ServiceEntityType('skill_name', 'skill_name',
                                        'skill_name', ['skill_name', 'spoken_name', 'account_type']))
