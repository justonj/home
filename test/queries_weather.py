weather_find_queries = [
    'what is the temperature in Los Angles',
    'is it too hot today',
    'whats the forecast for today',
]

weather_alert_queries = [
    'alert me if it is raining',
    'alert me if it is sunny day in bangalore'
]

weather_find_mentions = [
    [
        {
            'value': 'temperature',
            'field_id': 'weather_find_condition',
            'type': 'weather_condition'
        },
        {
            'field_id': 'place_or_day',
            'type': 'alias',
            'value': 'los angles'
        }
    ],
    [
        {
            'value': 'hot',
            'field_id': 'weather_find_condition',
            'type': 'weather_condition'
        },
        {
            'field_id': 'date_range',
            'type': 'alias',
            'value': 'today'
        }
    ],
    [
        {
            'field_id': 'date_range',
            'type': 'alias',
            'value': 'today'
        }
    ]
]

weather_alert_mentions = [
    [
        {
            'value': 'raining',
            'field_id': 'weather_find_condition',
            'type': 'weather_condition'
        }
    ],
    [
        {
            'value': 'sunny day',
            'field_id': 'weather_find_condition',
            'type': 'weather_condition'
        },
        {
            'field_id': 'location',
            'type': 'address',
            'value': 'bangalore'
        }
    ],
]
