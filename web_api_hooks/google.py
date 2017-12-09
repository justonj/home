from __future__ import print_function
import requests
from config import config
import time
from datetime import datetime
from collections import namedtuple
import re
from nlu.profiling import zipkin_trace
from .bounding_box_simple import get_bounding_box

Geocode = namedtuple(
    'Geocode', ['lat', 'lon', 'address_type', 'resolved_address'])
ignored_pattern = r'(xgl|xgm|xms|xsy|xtw|xwm|xwy|XGL|XGM|XMS|XSY|XTW|XWM|XWY)$'
_session = requests.Session()

RADIUS = 100  # radius in km


@zipkin_trace
def geocode(location_string, location=None):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    location_string = location_string.strip()
    # replace ignored pattern codes at end with empty string
    print('location original:', location_string)
    location_string = re.sub(ignored_pattern, '', location_string)
    print('location truncated:', location_string)
    params = {'address': location_string, 'key': config.GOOGLE_API_KEY}
    if location:
        params.update({'bounds': "%s,%s | %s,%s" %
                       get_bounding_box(RADIUS, location)})
    response = _session.get(url, params=params)
    try:
        data = response.json()['results'][0]
        loc = data['geometry']['location']
        address_type = data['geometry']['location_type']
        resolved_address = data['formatted_address']
        return Geocode(loc['lat'], loc['lng'], address_type, resolved_address)
    except (IndexError, KeyError, TypeError) as e:
        print("Failed to geocode location:", e)
        return None


@zipkin_trace
def reverse_geocode(lat, lon):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    latlng = "{0}, {1}".format(lat, lon)
    params = {'latlng': latlng, 'key': config.GOOGLE_API_KEY}
    response = _session.get(url, params=params)
    try:
        data = response.json()['results'][0]
        loc = data['geometry']['location']
        address_type = data['geometry']['location_type']
        resolved_address = data['formatted_address']
        return Geocode(loc['lat'], loc['lng'], address_type, resolved_address)
    except (IndexError, KeyError, TypeError) as e:
        print("Failed to reverse geocode:", e)
        return None


@zipkin_trace
def get_location_time(lat, lon):
    url = 'https://maps.googleapis.com/maps/api/timezone/json'
    timestamp = time.time()
    params = {
        'timestamp': timestamp,
        'location': '%s,%s' % (lat, lon),
        'key': config.GOOGLE_API_KEY
    }
    response = _session.get(url, params=params)
    try:
        response_data = response.json()
        offset = response_data['dstOffset'] + response_data['rawOffset']
        return datetime.utcfromtimestamp(timestamp + offset)
    except KeyError as e:
        print("Failed to get timezone:", e)
        return None
