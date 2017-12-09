import numpy as np

RADIUS_OF_EARTH_IN_KM = 6371.01
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0


def get_bounding_box(distance, location):
    """
    Given a Geographic co-ordintate in degress, aim is to get a bounding box of a given point,
    basically a maximum latitude, minmun latitude and max longitude and min longitude based on explanation
    and formulae by these two sites
    http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
    http://gis.stackexchange.com/questions/19221/find-tangent-point-on-circle-furthest-east-or-west

    :param distance: bounding box distance in kilometer
    :param latittude: of the point of the center of the box
    :param longitude: of the point of the center of the box
    :return: top left co-ordinates, and top-right co-ordinates of the bounding box
    """
    # Convert to radians
    latittude = np.radians(location[0])
    longitude = np.radians(location[1])

    if not MIN_LATITUDE <= latittude <= MAX_LATITUDE:
        return latittude, latittude, longitude, longitude

    if not MIN_LONGITUDE <= longitude <= MAX_LONGITUDE:
        return latittude, latittude, longitude, longitude

    distance_from_point_km = distance
    angular_distance = distance_from_point_km / RADIUS_OF_EARTH_IN_KM

    # Moving along a latitude north or south, keeping the longitude fixed, is travelling along
    # a great circle; which means basically that doing so,the Radius from center of the earth ,
    # to the circle traced by such a path is constant; So to derive the top latitude and bottom latitude
    # without any error you just need to add or suntract the angular distance
    lat_min = latittude - angular_distance
    lat_max = latittude + angular_distance

    # Handle poles here
    if lat_min < MIN_LATITUDE or lat_max > MAX_LATITUDE:
        lat_min = max(lat_min, MIN_LATITUDE)
        lat_max = min(lat_max, MAX_LATITUDE)
        lon_max = MAX_LONGITUDE
        lon_min = MIN_LONGITUDE
        lat_max = np.degrees(lat_max)
        lat_min = np.degrees(lat_min)
        lon_max = np.degrees(lon_max)
        lon_min = np.degrees(lon_min)
        return lat_min, lon_min, lat_max, lon_max

    # the latitude which intersects T1 and T2 in [1] and [2] is based on speherical trignomerty
    # this is just calculated for verifying this method
    latitude_of_intersection = np.arcsin(
        np.sin(latittude) / np.cos(angular_distance))
    latitude_of_intersection = np.degrees(latitude_of_intersection)

    # if we draw a circle  with distance around the lat and longitude, then the point where the
    # logitude touches the circle will be at a latitude a bit apart from the original latitiude as the
    # circle is on the sphere , the earths sphere
    delta_longitude = np.arcsin(np.sin(angular_distance) / np.cos(latittude))

    lon_min = longitude - delta_longitude
    lon_max = longitude + delta_longitude
    lon_min = np.degrees(lon_min)
    lat_max = np.degrees(lat_max)
    lon_max = np.degrees(lon_max)
    lat_min = np.degrees(lat_min)
    return lat_min, lon_min, lat_max, lon_max
