reservation_queries = [
    'book a table there for 2 PM today',
    # 'make a reservation there tomorrow',
    'make a reservation for ten people there',
    'reserve a table for 2 people at 5 PM',
    'A table for 4 around 7 pm tonight'
]

reservation_mentions = [
    [
        {'value': 'there', 'field_id': 'venue', 'type': 'local_business'},
        {'value': '2', 'field_id': 'num_people', 'type': 'number'},
        {'value': 'today', 'field_id': 'date', 'type': 'date'}
    ],
    # [
    #     {'value': 'there', 'field_id': 'venue', 'type': 'local_business'},
    #     {'value': 'tomorrow', 'field_id': 'date', 'type': 'date'}
    # ],
    [
        {'value': 'ten', 'field_id': 'num_people', 'type': 'number'},
        {'value': 'there', 'field_id': 'venue', 'type': 'local_business'}
    ],
    [
        {'value': '2', 'field_id': 'num_people', 'type': 'number'},
        {'value': '5 pm', 'field_id': 'time', 'type': 'time'}
    ],
    [
        {'value': '4', 'field_id': 'num_people', 'type': 'number'},
        {'value': '7 pm', 'field_id': 'time', 'type': 'time'},
        {'value': 'tonight', 'field_id': 'date', 'type': 'date'}

    ]
]
