import requests_mock
import pytest
import json

from nlu.dialogue_system.test_utils import assert_context_conversation_deterministic_features, create_payload, \
    create_expected_output, create_context
from nlu.skills.skill_manager import get_skill


play_hello_response = open(pytest.SAMPLE_DATA_PATH +
                           "/music/music_play_hello.json").read()
play_hello_response_dict = json.loads(play_hello_response)

play_justin_bieber_response = open(
    pytest.SAMPLE_DATA_PATH + "/music/music_play_justin_bieber.json").read()
play_justin_bieber_response_dict = json.loads(play_justin_bieber_response)

MUSIC_SKILL_URL = get_skill('music').url + '/retrieve'
CONCERT_SKILL_URL = get_skill('concert').url + '/retrieve'


@requests_mock.Mocker(kw='mock')
class TestCrossDomain:
    drm = None
    model_name = 'aneeda_en'

    def setup_class(self):
        assert hasattr(pytest.response_managers, self.model_name)
        self.drm = getattr(pytest.response_managers, self.model_name)
        self.drm.add_intent_dialogue_rule(
            'music_play', 'Boom Here you go', None)
        self.drm.add_intent_dialogue_rule(
            'music_info_similar_artists', 'Check out similar artists', None)
        self.drm.add_intent_dialogue_rule(
            'music_albums', 'Here\'s all the albums', None)
        self.drm.add_intent_dialogue_rule(
            'music_info_concerts', 'Lemme see', None)

    def teardown_class(self):
        self.drm.clear_rules()

    def test_song_to_album(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        followup_program = play_hello_response_dict['fields']['tracks']['items'][0]
        music_album = followup_program.get('album')
        assert_context_conversation_deterministic_features(
            self.model_name,
            self.drm,
            None,
            (create_payload('Play the song hello'), 'music_play', {'song': 'hello'}),
             create_expected_output('Boom Here you go'),
            (create_payload('play this album', display_context=create_context(list_id='hello_response', index_id='49422899')),
                            'music_play', {'album': 'this'}),
             create_expected_output(
                'Boom Here you go',
                fields={
                    "album":{
                        'id': music_album.get('id'),
                        'name': music_album.get('name'),
                        'type': music_album.get('type'),
                        'artist': music_album.get('artist'),
                        'spoken_name': followup_program.get('name') +
                                       ' by ' +
                                       music_album.get('artist').get('name'),
                        'type': 'music_album',
                        'user_input': 'this'
                    }
                }
             )
        )

    def test_song_to_similar_artists(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )

        followup_program = play_hello_response_dict['fields']['tracks']['items'][0]
        music_artist = followup_program.get('album').get('artist')
        music_artist['user_input'] = 'this performer'
        assert_context_conversation_deterministic_features(
            self.model_name,
            self.drm,
            None,
            (create_payload('Play the song hello'), 'music_play', {'song' : 'hello'}),
             create_expected_output('Boom Here you go'),
            (create_payload('Find artists similar to this performer',
                            display_context=create_context(list_id='hello_response', index_id='49422899')),
                            'music_info_similar_artists', {'artist': 'this performer'}),
             create_expected_output(
                'Check out similar artists',
                fields={
                    "artist": music_artist
                }
             )
        )

    def test_artist_to_albums(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_justin_bieber_response
        )

        followup_program = play_justin_bieber_response_dict['fields']['tracks']['items'][0]
        music_artist = followup_program.get('album').get('artist')
        assert_context_conversation_deterministic_features(
            self.model_name,
            self.drm,
            None,
            (create_payload('Play Justin Bieber'), 'music_play', {'artist': 'justin bieber'}),
             create_expected_output('Boom Here you go'),
            (create_payload('what were his albums',
                            display_context=create_context(list_id='hello_response', index_id='49422899')),
                            'music_albums', {'artist': 'his'}),
             create_expected_output(
                'Here\'s all the albums',
                fields={
                    "artist":{
                        'id': music_artist.get('id'),
                        'name': music_artist.get('name').lower(),
                        'popularity': 0.94,
                        'type': 'music_artist',
                        'user_input': 'his'
                    }
                }
             )
        )

    #@pytest.mark.skip(reason='Getting classified as sports skill.')
    def test_song_to_concerts(self, **kwargs):
        m = kwargs['mock']
        m.register_uri(
            'POST',
            MUSIC_SKILL_URL,
            text=play_hello_response
        )
        m.register_uri(
            'POST',
            CONCERT_SKILL_URL,
            text=play_hello_response
        )

        followup_program = play_hello_response_dict['fields']['tracks']['items'][0]
        music_artist = followup_program.get('album').get('artist')
        print('music_artist:', music_artist)
        assert_context_conversation_deterministic_features(
            self.model_name,
            self.drm,
            None,
            (create_payload('Play the song hello'), 'music_play', {'song': 'hello'}),
             create_expected_output('Boom Here you go'),
            (create_payload('When are they playing?',
                            display_context=create_context(list_id='hello_response', index_id='49422899')),
                            'music_info_concerts', {'artist': 'they'}),
             create_expected_output(
                'Lemme see',
                fields={
                    "artist":{
                        'id': music_artist.get('id'),
                        'name': music_artist.get('name'),
                        'type': music_artist.get('type'),
                        'popularity': music_artist.get('popularity'),
                        'user_input': 'they'
                    }
                }
             )
        )
