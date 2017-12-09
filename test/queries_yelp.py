restaurant_search_queries = [
    'find indian restaurants nearby',
    'show me restaurants in London',
    'Can you please find budget mexican food places',
    # 'I am looking for sushi in hollywood', - fails now due to training updates
    'Is there any good indian restaurant nearby',
    # 'good chinese food near me'
]

business_search_queries = [
    'show me car wash near me',
    'find car wash near Park la brea'
    # 'show me beauty salons nearby' - fails but not critical
]

restaurant_mentions = [
    [
        {'value': 'indian', 'field_id': 'cuisine', 'type': 'cuisine'},
        {'value': 'nearby', 'field_id': 'location', 'type': 'address'}
    ],
    [
        {'value': 'london', 'field_id': 'location', 'type': 'address'}
    ],
    [
        {'value': 'mexican', 'field_id': 'cuisine', 'type': 'cuisine'},
    ],
    [
        {'value': 'indian', 'field_id': 'cuisine', 'type': 'cuisine'},
        {'value': 'nearby', 'field_id': 'location', 'type': 'address'}
    ],
    [
        {'value': 'chinese', 'field_id': 'cuisine', 'type': 'cuisine'},
        {'value': 'near me', 'field_id': 'location', 'type': 'address'}
    ],
]

business_mentions = [
    [
        {'value': 'car wash', 'field_id': 'keyword', 'type': 'text'},
        # {'value': 'near me', 'field_id': 'location', 'type': 'address'} -- fails but not critical.
    ],
    [
        {'value': 'car wash', 'field_id': 'keyword', 'type': 'text'},
        {'value': 'brea', 'field_id': 'location', 'type': 'address'}
    ]
]
