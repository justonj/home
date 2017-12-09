from nlu.evaluation.sampling import StratificationFilter, \
    register_stratification_filter

# Here you can define sample stratification rules, which will be applied to
# samples through the sample framework.
# The intended use is to ensure that the data used in significantly variant
# and direct the bootstrapping procedure
# Below you can see some examples of some stratification filters and
# how to register them.

SPORTS_INTENTS = ['sports_follow_a_game',
                  'sports_team_results',
                  'sports_team_schedule',
                  'sports_team_standing']


def has_entity_data(entity_data, field):
    return field in entity_data and entity_data[field] != []


def sports_team_filter(data_row):
    entity_data = data_row.get_original_observation().get_annotations()
    mentions_team_bool = has_entity_data(entity_data,'team_name')
    mentions_team_1_bool = has_entity_data(entity_data,'team_name_1')
    mentions_team_2_bool = has_entity_data(entity_data, 'team_name_2')
    return mentions_team_bool or mentions_team_1_bool or mentions_team_2_bool


def sports_team_second_filter(data_row):
    return True


def div_league_conf_filter(data_row):
    entity_data = data_row.get_original_observation().get_annotations()
    division_bool = has_entity_data(entity_data, 'division_name')
    league_bool = has_entity_data(entity_data, 'league_name')
    conference_bool = has_entity_data(entity_data, 'conference_name')
    return division_bool or league_bool or conference_bool


def sports_long_balancer(data_row):
    response = data_row.get_original_observation().get_tokenized()
    return len(response) > 12


def sports_short_balancer(data_row):
    response = data_row.get_original_observation().get_tokenized()
    return len(response) < 6


def sports_game_frequency(data_row):
    response = data_row.get_original_observation().get_tokenized()

    return not('game' in response)

# instantiate a new stratification filters for the play music intent

sports_team_frequency_filter = StratificationFilter(
    'sports_team_frequency',
    sports_team_filter, .6)

div_league_conf_frequency_filter = StratificationFilter(
    'div_league_conf_frequency',
    div_league_conf_filter, .20)

sports_game_frequency_filter = StratificationFilter(
    'sports_game_frequency',
    sports_game_frequency, .15)

long_balancer_filter = StratificationFilter(
    'sports_long_balancer',
    sports_long_balancer, .15)

short_balancer_filter = StratificationFilter(
    'sports_short_balancer',
    sports_short_balancer, .25)

# register our filter for use with the sampling framework in as many intents
# as you like
for intent in SPORTS_INTENTS:
    register_stratification_filter(sports_team_frequency_filter,
                                   'crf_model', intent)
    register_stratification_filter(div_league_conf_frequency_filter,
                                   'intent_classifier', intent)
    register_stratification_filter(div_league_conf_frequency_filter,
                                   'crf_model', intent)
    register_stratification_filter(div_league_conf_frequency_filter,
                                   'intent_classifier', intent)
    register_stratification_filter(long_balancer_filter,
                                   'crf_model', intent)
    register_stratification_filter(long_balancer_filter,
                                   'intent_classifier', intent)
    register_stratification_filter(short_balancer_filter,
                                   'crf_model', intent)
    register_stratification_filter(short_balancer_filter,
                                   'intent_classifier', intent)

register_stratification_filter(
    sports_game_frequency_filter,
    'crf_model', 'sports_team_results')

register_stratification_filter(
    sports_game_frequency_filter,
    'intent_classifier',
    'sports_team_results')
