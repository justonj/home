listings_queries = [
    'find action movies on sunday morning',
    'Find sports that are playing now',
    'What shows are on at 10 o\'clock tonight?',
    'find comedy shows for me to watch',
    'find some kids friendly tv shows',
    'find me some handball shows',
    'whats on mtv at 9p.m',
    'whats on hbo at 9 p.m' #before trained - extraction
]

show_cast_queries = [
    'Whats the cast of The Price Is Right',
    'find the cast of the get down',
    #'who is in people magazine investigates',
    #'Who is in the show Secrets of the Dead',
    'who appears in To Tell the Truth'
]

show_description_queries = [
    'What is Westworld about?',
    'What\'s the show Supergirl about',
    'Describe Shameless to me',
    #'What is Ash vs. Evil Dead about?',
    'what is conan the adventurer about',
    'Whats the show the affair about',
    'whats the show the exorcist about',
    'Tell me about The Rule',
    'Find me the description of rock the park',
    'Tell me about The Guardians',
    #'Tell me about The Cowboy', #before trained-classification
    'Tell me about show Hitler',
    'Give me the plot of teen wolf',
    'show me the description of gravity falls',
    'Description of the show Sofia the First',
    #'tell me about the beat', #before trained - classification
    'search for people magazine investigates show description',
    'Describe grilling with philips to me',
    'Summarize the tv show joseph prince',
    'Description of the show Wheel of Fortune',
    'search for moonshiners show description',
    'Find the synopsis of father brown',
    'find the description of the show leverage',
    'Give me the description of the show riptide',
    'describe mad money to me',
    #'what is Let\'s Make a Deal about' #before trained - extraction
]

show_episode_summary_queries = [
    'Whats the next episode of long lost family about ?',
    # 'what happens in The Texas Bucket List this week',
    # 'show me whats up on Meet the Press this week',
    # 'whats on The Coolest Places on Earth next week',
    # 'Whats on the soul man next week',
    # 'whats on The Amazing World of Gumball next week',
    # 'What happens in Highly Questionable this week',
    #'Give me a summary of the newest episode of the 700 club ?' #before trained - extraction
]

listings_mentions = [
    [
        {'value': 'action', 'field_id': 'genre', 'type': 'tv_genre'},
        {'value': 'movies', 'field_id': 'type', 'type': 'tv_type'},
        {'value': 'sunday', 'field_id': 'date', 'type': 'date'},
        {'value': 'morning', 'field_id': 'time', 'type': 'time'},
    ],
    [
        {'value': 'sports', 'field_id': 'type', 'type': 'tv_type'}
    ],
    [
        {'value': '10 o\'clock tonight', 'field_id': 'time', 'type': 'time'}
    ],
    [
        {'value': 'comedy', 'field_id': 'genre', 'type': 'tv_genre'}
    ],
    [
        {'value': 'kids', 'field_id': 'genre', 'type': 'tv_genre'}
    ],
    [
        {'value': 'handball', 'field_id': 'genre', 'type': 'tv_genre'}
    ],
    [
        {'value': 'mtv', 'field_id': 'channel', 'type': 'tv_channel_name'},
        {'value': '9p.m', 'field_id': 'time', 'type': 'time'}
    ],
    [
        {'value': 'hbo', 'field_id': 'channel', 'type': 'tv_channel_name'},
        {'value': '9 p.m', 'field_id': 'time', 'type': 'time'}
    ]
]

show_cast_mentions = [
    [
        {'value': 'the price is right', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the get down', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    # [
    #     {'value': 'people magazine investigates', 'field_id': 'show', 'type': 'tv_show_name'}
    # ],
    # [
    #     {'value': 'secrets of the dead', 'field_id': 'show', 'type': 'tv_show_name'}
    # ],
    [
        {'value': 'to tell the truth', 'field_id': 'show', 'type': 'tv_show_name'}
    ]
]

show_description_mentions = [
    [
        {'value': 'westworld', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'supergirl', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'shameless', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    # [
    #     {'value': 'ash vs evil dead', 'field_id': 'show', 'type': 'tv_show_name'}
    # ],
    [
        {'value': 'conan the adventurer', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the affair', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the exorcist', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the rule', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'rock the park', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the guardians', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    # [
    #     {'value': 'the cowboy', 'field_id': 'show', 'type': 'tv_show_name'}
    # ],
    [
        {'value': 'hitler', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'teen wolf', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'gravity falls', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'sofia the first', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    # [
    #     {'value': 'the beat', 'field_id': 'show', 'type': 'tv_show_name'}
    # ],
    [
        {'value': 'people magazine investigates', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'grilling with philips', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'joseph prince', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'wheel of fortune', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'moonshiners', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'father brown', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'leverage', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'riptide', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'mad money', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    # [
    #     {'value': 'let\'s make a deal', 'field_id': 'show', 'type': 'tv_show_name'}
    # ]

]

show_episode_summary_mentions = [
    [
        {'field_id': 'showrelative', 'type': 'showrelative', 'value': 'next'},
        {'value': 'long lost family', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the texas bucket list', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'meet the press', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the coolest places on earth', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the soul man', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'the amazing world of gumball', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    [
        {'value': 'highly questionable', 'field_id': 'show', 'type': 'tv_show_name'}
    ],
    # [
    #     {'value': 'the 700 club', 'field_id': 'show', 'type': 'tv_show_name'}
    # ]
]