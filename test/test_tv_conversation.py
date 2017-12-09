import requests_mock
import pytest
import json

from nlu.dialogue_system.test_utils import assert_conversation_features, create_payload, \
    create_expected_output
from nlu.skills.skill_manager import get_skill

programs_response = open(pytest.SAMPLE_DATA_PATH +
                         "/tv/tv_listings.json").read()
programs_response_dict = json.loads(programs_response)

cast_response = open(pytest.SAMPLE_DATA_PATH + "/tv/tv_show_cast.json").read()
cast_response_dict = json.loads(cast_response)


TV_SKILL_URL = get_skill('tv').url + '/retrieve'

@pytest.mark.skip(reason="TV skill training file is disabled")
@requests_mock.Mocker(kw='mock')
class TestCrossDomain:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        self.drm.add_intent_dialogue_rule(
            'tv_listings', 'Here are programs', None)
        self.drm.add_intent_dialogue_rule('tv_show_cast', 'Here is cast', None)
        self.drm.add_intent_dialogue_rule(
            'calendar_create_event', 'Event created', None)
        self.drm.add_intent_dialogue_rule(
            'tv_show_episode_summary', 'Here is episode summary', None)

    def teardown_class(self):
        self.drm.clear_rules()

    def test_tv_listings_to_cast_trigger(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            TV_SKILL_URL,
            text=programs_response
        )

        followup_program = programs_response_dict['entities'][0]
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('whats on mtv'),
             create_expected_output('Here are programs')),
            (create_payload('who stars in this one',
                            card_token="123"),
             create_expected_output(
                 'Here is cast',
                 mentions=[
                     {
                         'gracenote_name': followup_program.get('title'),
                         'resolved': True,
                         'user_provided': True,
                         'tv_show_name': followup_program.get('title'),
                         'spoken_name': followup_program.get('title'),
                         'field_id': 'show',
                         'type': 'tv_show_name',
                         'value': 'this one'
                     }
                 ]
            ))
        )

    def test_tv_listings_to_cast_list_trigger(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            TV_SKILL_URL,
            text=programs_response
        )

        followup_program = programs_response_dict['entities'][1]
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('whats on mtv'),
             create_expected_output('Here are programs')),
            (create_payload('who stars in second one',
                            card_token=followup_program.get('card_token')),
             create_expected_output(
                 'Here is cast',
                 mentions=[
                     {
                         'gracenote_name': followup_program.get('title'),
                         'resolved': True,
                         'user_provided': True,
                         'tv_show_name': followup_program.get('title'),
                         'spoken_name': followup_program.get('title'),
                         'field_id': 'show',
                         'type': 'tv_show_name',
                         'value': 'second'
                     }
                 ]
            ))
        )

    def test_tv_listings_to_calendar_trigger(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            TV_SKILL_URL,
            text=programs_response
        )

        followup_program = programs_response_dict['entities'][1]
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('whats on mtv'),
             create_expected_output('Here are programs')),
            (create_payload('add this to my calendar',
                            card_token=followup_program.get('card_token')),
             create_expected_output(
                 'Event created',
                 mentions=[
                     {
                         'entity': {
                             'datetime': followup_program.get('datetime'),
                             'title': followup_program.get('title'),
                             'duration': followup_program.get('duration')
                         },
                         'field_id': 'event',
                         'type': 'event',
                         'value': 'this',
                         'user_provided': True
                     }
                 ]
            ))
        )

    def test_tv_listings_to_calendar_list_trigger(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            TV_SKILL_URL,
            text=programs_response
        )

        followup_program = programs_response_dict['entities'][0]
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('whats on mtv'),
             create_expected_output('Here are programs')),
            (create_payload('add first one to my calendar',
                            card_token=""),
             create_expected_output(
                 'Event created',
                 mentions=[
                     {
                         'entity': {
                             'datetime': followup_program.get('datetime'),
                             'title': followup_program.get('title'),
                             'duration': followup_program.get('duration')
                         },
                         'field_id': 'event',
                         'type': 'event',
                         'value': 'first one',
                         'user_provided': True
                     }
                 ]
            ))
        )

    def test_tv_cast_to_episode_summary(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            TV_SKILL_URL,
            text=cast_response
        )

        followup_program = cast_response_dict['entities'][0]
        assert_conversation_features(
            self.model_name,
            self.drm,
            (create_payload('who is in the cast of Modern Family'),
             create_expected_output('Here is cast')),
            (create_payload('what is on the next episode of this',
                            card_token=followup_program.get('card_token')),
             create_expected_output(
                 'Here is episode summary',
                 mentions=[
                     {
                         'gracenote_name': followup_program.get('tv_show_name', {}).get('gracenote_name'),
                         'resolved': True,
                         'user_provided': True,
                         'tv_show_name': followup_program.get('tv_show_name', {}).get('tv_show_name'),
                         'spoken_name': followup_program.get('tv_show_name', {}).get('tv_show_name'),
                         'field_id': 'show',
                         'type': 'tv_show_name',
                         'value': 'this'
                     }
                 ]
            ))
        )
