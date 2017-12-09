from config import config

from nlu.knowledge_base.knowledge_retrieval_manager import register_retrieval_rule
from nlu.knowledge_base.knowledge_retrieval_manager import WebHookRule

_movie_showtimes_hook_id = 'get_movie_showtimes'
_movie_showtimes_precondition = ['movie']
_movie_showtimes_fields = ['movie_listings']
_movie_showtimes_entity_types = {'movie_listings': 'list<local_business>'}

_get_movie_showtimes = WebHookRule(
    'movies_showtimes', 'blank_en',
    _movie_showtimes_hook_id,
    _movie_showtimes_precondition,
    result_fields=_movie_showtimes_fields,
    entity_types=_movie_showtimes_entity_types)

_get_origin_transport_book = WebHookRule(
    'transport_taxi_book', 'blank_en',
    'get_current_origin',
    [],
    result_fields=['origin'],
    entity_types={'origin': 'address'},
    standard_output=False)

_get_origin_transport_current_status = WebHookRule(
    'transport_taxi_current_status', 'blank_en',
    'get_current_origin',
    [],
    result_fields=['origin'],
    entity_types={'origin': 'address'},
    standard_output=False)

_get_origin_transport_estimate_fare = WebHookRule(
    'transport_taxi_estimate_travel_fare', 'blank_en',
    'get_current_origin',
    [],
    result_fields=['origin'],
    entity_types={'origin': 'address'},
    standard_output=False)

_get_origin_transport_estimate_time = WebHookRule(
    'transport_taxi_estimate_travel_time', 'blank_en',
    'get_current_origin',
    [],
    result_fields=['origin'],
    entity_types={'origin': 'address'},
    standard_output=False)

_get_origin_maps_nav_directions = WebHookRule(
    'maps_nav_directions', 'blank_en',
    'get_current_origin',
    [],
    result_fields=['origin'],
    entity_types={'origin': 'address'},
    standard_output=False)

_get_origin_maps_nav_travel_time_to = WebHookRule(
    'maps_nav_travel_time_to',
    'blank_en',
    'get_current_origin',
    [],
    result_fields=['origin'],
    entity_types={'origin': 'address'},
    standard_output=False)

pool_result_fields = ['is_pool']
pool_entity_types = {'is_pool': 'boolean'}

_transport_taxi_book_is_pool = WebHookRule(
    'transport_taxi_book', 'blank_en',
    'transport_is_pool', ['taxi_service_id'],
    result_fields=pool_result_fields,
    entity_types=pool_entity_types,
    standard_output=False)

_transport_taxi_estimate_fare_is_pool = WebHookRule(
    'transport_taxi_estimate_travel_fare', 'blank_en',
    'transport_is_pool', ['taxi_service_id'],
    result_fields=pool_result_fields,
    entity_types=pool_entity_types,
    standard_output=False)


_get_location_weather_find = WebHookRule(
    'weather_find', 'blank_en',
    'get_current_location',
    [],
    result_fields=['location'],
    entity_types={'location': 'address'},
    standard_output=False)

_get_location_weather_set_alert = WebHookRule(
    'weather_set_alert', 'blank_en',
    'get_current_location',
    [],
    result_fields=['location'],
    entity_types={'location': 'address'},
    standard_output=False)

_get_location_yelp_restaurants = WebHookRule(
    'restaurant_search', 'blank_en',
    'get_current_location',
    [],
    result_fields=['location'],
    entity_types={'location': 'address'},
    standard_output=False)

_get_location_yelp_business = WebHookRule(
    'business_search', 'blank_en',
    'get_current_location',
    [],
    result_fields=['location'],
    entity_types={'location': 'address'},
    standard_output=False)

_restaurant_reservation_user_info = WebHookRule(
    'restaurant_reservation',
    'blank_en',
    'ares_user_info',
    fields_precondition=['venue', 'num_people', 'date', 'time'],
    result_fields=['user_name', 'user_id', 'user_phone_number'],
    entity_types={
        'user_name': 'text',
        'user_id': 'text',
        'user_phone_number': 'phone_number'
    },
    rewrite_dialogue_state=True
)

_start_ares_reservation = WebHookRule(
    'restaurant_reservation',
    'blank_en',
    'start_ares_reservation',
    fields_precondition=['venue', 'num_people', 'date',
                         'time', 'user_id', 'user_phone_number'],
    result_fields=['result'],
    entity_types={'result': 'boolean'}
)

_get_tv_channel_listing = WebHookRule(
    'tv_listings',
    'blank_en',
    'get_tv_listing',
    fields_precondition=['channel', 'zipcode'],
    result_fields=['tv_listing', 'metadata'],
    entity_types={'tv_listing': 'list<program>',
                  'metadata': 'json'}
)

_get_tv_genre_listing = WebHookRule(
    'tv_listings',
    'blank_en',
    'get_tv_listing',
    fields_precondition=['genre', 'zipcode'],
    result_fields=['tv_listing', 'metadata'],
    entity_types={'tv_listing': 'list<program>',
                  'metadata': 'json'}
)

_get_tv_cast_listing = WebHookRule(
    'tv_show_cast',
    'blank_en',
    'get_tv_listing',
    fields_precondition=['show'],
    result_fields=['tv_listing', 'metadata'],
    entity_types={'tv_listing': 'list<program>',
                  'metadata': 'json'}
)

_get_tv_description_listing = WebHookRule(
    'tv_show_description',
    'blank_en',
    'get_tv_listing',
    fields_precondition=['show'],
    result_fields=['tv_listing', 'metadata'],
    entity_types={'tv_listing': 'list<program>',
                  'metadata': 'json'}
)

_get_tv_episode_summary_listing = WebHookRule(
    'tv_show_episode_summary',
    'blank_en',
    'get_tv_listing',
    fields_precondition=['show'],
    result_fields=['tv_listing', 'metadata'],
    entity_types={'tv_listing': 'list<program>',
                  'metadata': 'json'}
)

_get_tv_show_airings_listing = WebHookRule(
    'tv_show_airings',
    'blank_en',
    'get_tv_listing',
    fields_precondition=['show'],
    result_fields=['tv_listing', 'metadata'],
    entity_types={'tv_listing': 'list<program>',
                  'metadata': 'json'}
)

_get_tv_streaming_search_listing = WebHookRule(
    'tv_streaming_search',
    'blank_en',
    'get_tv_listing',
    fields_precondition=['show'],
    result_fields=['tv_listing', 'metadata'],
    entity_types={'tv_listing': 'list<program>',
                  'metadata': 'json'}
)

_get_business_address = WebHookRule(
    'business_address',
    'blank_en',
    'get_local_business_address',
    fields_precondition=['business'],
    result_fields=['business_address'],
    entity_types={'business_address': 'address'},
    standard_output=False
)

_get_business_reviews = WebHookRule(
    'business_reviews',
    'blank_en',
    'get_local_business_reviews',
    fields_precondition=['business'],
    result_fields=['business_reviews'],
    entity_types={'business_reviews': 'reviews'},
    standard_output=False
)

_get_business_rating = WebHookRule(
    'business_rating',
    'blank_en',
    'get_local_business_rating',
    fields_precondition=['business'],
    result_fields=['business_rating'],
    entity_types={'business_rating': 'number'},
)

_get_business_price = WebHookRule(
    'business_price',
    'blank_en',
    'get_local_business_price',
    fields_precondition=['business'],
    result_fields=['business_price'],
    entity_types={'business_price': 'price'},
)

_get_business_phone = WebHookRule(
    'business_phone',
    'blank_en',
    'get_local_business_phone',
    fields_precondition=['business'],
    result_fields=['business_phone'],
    entity_types={'business_phone': 'phone_number'},
)

_get_business_hours = WebHookRule(
    'business_hours',
    'blank_en',
    'get_local_business_hours',
    fields_precondition=['business'],
    result_fields=['business_hours'],
    entity_types={'business_hours': 'hours',
                  'open_now': 'boolean'},
    standard_output=False
)

_email_compose_account_present_rule = WebHookRule(
    'email_compose',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)

_email_compose_account_config_check_rule = WebHookRule(
   'email_compose',
   'blank_en',
   'user_accounts_config_check',
   fields_precondition=[],
   result_fields=['is_any_email_acc_configured', 'email_from_account'],
   entity_types={'is_any_email_acc_configured': 'yes_no',
                 'email_from_account': 'skill_name'},
   standard_output=False)

_email_show_account_present_rule = WebHookRule(
    'email_show',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)

_email_summarize_account_present_rule = WebHookRule(
    'email_summarize',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)

_email_check_account_present_rule = WebHookRule(
    'email_check',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)

_email_reply_account_present_rule = WebHookRule(
    'email_reply',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)

_calendar_check_account_present_rule = WebHookRule(
    'calendar_check_event',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)

_calendar_create_account_present_rule = WebHookRule(
    'calendar_create_event',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)

_calendar_show_account_present_rule = WebHookRule(
    'calendar_show_event',
    'blank_en',
    'user_account_check',
    fields_precondition=[],
    result_fields=['email_error'],
    entity_types={'email_error': 'error'},
    standard_output=False)


if config.ENABLE_WEBHOOKS:
    print("Registering hooks")
    register_retrieval_rule(_get_movie_showtimes)

    # Order of webhooks registered in uber should not be changed
    register_retrieval_rule(_get_origin_transport_book)
    register_retrieval_rule(_get_origin_transport_estimate_fare)
    register_retrieval_rule(_get_origin_transport_estimate_time)
    register_retrieval_rule(_transport_taxi_book_is_pool)
    register_retrieval_rule(_transport_taxi_estimate_fare_is_pool)
    register_retrieval_rule(_get_origin_transport_current_status)
    register_retrieval_rule(_get_origin_maps_nav_directions)
    register_retrieval_rule(_get_origin_maps_nav_travel_time_to)

    register_retrieval_rule(_get_location_weather_find)
    register_retrieval_rule(_get_location_weather_set_alert)

    register_retrieval_rule(_restaurant_reservation_user_info)
    # register_retrieval_rule(_start_ares_reservation)

    register_retrieval_rule(_email_compose_account_present_rule)
    register_retrieval_rule(_email_compose_account_config_check_rule)
    register_retrieval_rule(_email_show_account_present_rule)
    register_retrieval_rule(_email_summarize_account_present_rule)
    register_retrieval_rule(_email_check_account_present_rule)
    register_retrieval_rule(_email_reply_account_present_rule)

    register_retrieval_rule(_calendar_check_account_present_rule)
    register_retrieval_rule(_calendar_create_account_present_rule)
    register_retrieval_rule(_calendar_show_account_present_rule)

    register_retrieval_rule(_get_location_yelp_business)
    register_retrieval_rule(_get_location_yelp_restaurants)

    register_retrieval_rule(_get_business_address)
    register_retrieval_rule(_get_business_rating)
    register_retrieval_rule(_get_business_hours)
    register_retrieval_rule(_get_business_reviews)
    register_retrieval_rule(_get_business_price)
    register_retrieval_rule(_get_business_phone)
