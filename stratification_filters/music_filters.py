from nlu.evaluation.sampling import StratificationFilter, \
    register_stratification_filter

# Here you can define sample stratification rules, which will be applied to
# samples through the sample framework.
# The intended use is to ensure that the data used in significantly variant and
# direct the bootstrapping procedure.
# Below you can see some examples of some stratification filters and
# how to register them.


def music_artist(data_row):
    entity_data = data_row.get_original_observation().get_annotations()
    return 'artist' in entity_data and entity_data['artist'] != []


def music_song(data_row):
    entity_data = data_row.get_original_observation().get_annotations()
    return 'song' in entity_data and entity_data['song'] != []


def music_album(data_row):
    entity_data = data_row.get_original_observation().get_annotations()
    return 'album' in entity_data and entity_data['album'] != []


def long_balancer(data_row):
    response = data_row.get_original_observation().get_tokenized()
    return len(response) > 10

def short_balancer(data_row):
    response = data_row.get_original_observation().get_tokenized()
    return len(response) < 5


def music_play_frequency(data_row):
    response = data_row.get_original_observation().get_tokenized()
    return not('play' in response)

# instantiate a new stratification filters for the play music intent
music_artist_filter = StratificationFilter('music_artist_filter',
                                           music_artist, .10)
music_song_filter = StratificationFilter('music_song_filter',
                                         music_song, .25)
music_album_filter = StratificationFilter('music_album_filter',
                                          music_album, .25)
music_play_frequency_filter = StratificationFilter('music_play_frequency',
                                                   music_play_frequency, .10)
long_balancer_filter = StratificationFilter('music_play_long_balancer',
                                            long_balancer, .15)
short_balancer_filter = StratificationFilter('music_play_short_balancer',
                                             short_balancer, .15)

# register our filter for use with the sampling framework in as many intents
# as you like

register_stratification_filter(music_artist_filter,
                               'crf_model', 'music_play')
register_stratification_filter(music_artist_filter,
                               'intent_classifier', 'music_play')
register_stratification_filter(music_artist_filter,
                               'synthesizer', 'music_play')

register_stratification_filter(music_song_filter,
                               'crf_model', 'music_play')
register_stratification_filter(music_song_filter,
                               'intent_classifier', 'music_play')
register_stratification_filter(music_song_filter,
                               'synthesizer', 'music_play')

register_stratification_filter(music_play_frequency_filter,
                               'crf_model', 'music_play')
register_stratification_filter(music_play_frequency_filter,
                               'intent_classifier', 'music_play')
register_stratification_filter(music_play_frequency_filter,
                               'synthesizer', 'music_play')

register_stratification_filter(long_balancer_filter,
                               'crf_model', 'music_play')
register_stratification_filter(long_balancer_filter,
                               'intent_classifier', 'music_play')
register_stratification_filter(long_balancer_filter,
                               'synthesizer', 'music_play')

register_stratification_filter(short_balancer_filter,
                               'crf_model', 'music_play')
register_stratification_filter(short_balancer_filter,
                               'intent_classifier', 'music_play')
register_stratification_filter(short_balancer_filter,
                               'synthesizer', 'music_play')
