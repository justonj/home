taxi_book_queries = [
    'book an uberx to santa monica',
    'book a ride',
    'take me to hollywood by uberx'
]

taxi_book_mentions = [
    [
        {
            "field_id": "taxi_service_id",
            "type": "transport_taxi_service_type",
            "value": "uberx"
        },
        {
            "field_id": "destination",
            "type": "custom_location_type",
            "value": "santa monica"
        }
    ],
    [],
    [
        {
            "field_id": "destination",
            "type": "custom_location_type",
            "value": "hollywood"
        },
        {
            "field_id": "taxi_service_id",
            "type": "transport_taxi_service_type",
            "value": "uberx"
        }
    ]

]


taxi_fare_queries = [
    'what is the fare to travel to santa monica',
    'how much does it cost to travel to hollywood from santa monica',
    'what is the cost to reach N.coheunga blvd'
]

taxi_fare_mentions = [
    [
        {
            "field_id": "destination",
            "type": "custom_location_type",
            "value": "santa monica"
        }
    ],
    [
        {
            "field_id": "destination",
            "type": "custom_location_type",
            "value": "hollywood"
        },
        {
            'field_id': 'origin',
            'type': 'custom_location_type',
            'value': 'santa monica'
        }
    ],
    [
        {
            "field_id": "destination",
            "type": "custom_location_type",
            "value": "n.coheunga blvd"
        }
    ]
]

taxi_duration_queries = [
    'what is the travel time to reach to hollywood',
]

taxi_duration_mentions = [
    [
        {
            "field_id": "destination",
            "type": "custom_location_type",
            "value": "hollywood"
        }
    ],
]

taxi_cancel_queries = [
    'cancel uberx',
    'tell uber to cancel my ride',
    'abort my ride'
]

taxi_cancel_mentions = [
    [
        {
            "field_id": "taxi_service_id",
            "type": "transport_taxi_service_type",
            "value": "uberx"
        }
    ],
    [
        {
            "field_id": "taxi_service_id",
            "type": "transport_taxi_service_type",
            "value": "uber"
        }
    ],
    []
]

taxi_current_status_queries = [
    'where is my uberx',
]

taxi_status_mentions = [
    [
        {
            "field_id": "taxi_service_id",
            "type": "transport_taxi_service_type",
            "value": "uberx"
        }
    ]
]

taxi_history_queries = {
    'show my previous rides',
    'my last ride history',
    'I want to see my record of Uber rides'
}
