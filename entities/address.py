from nlu.knowledge_base.entity_type_registry import register_entity_type
from nlu.knowledge_base.entity_type_base import EntityTypeBase, DEFAULT_VALUE_KEY
import nlu_applications.blank.web_api_hooks.google as google
from faker import Factory
from nlu.payload_utils import get_payload_location


class AddressType(EntityTypeBase):
    id = 'address'
    local_context_resolution_triggers = ['here', 'current location',
                                         'nearby', 'near me']
    fake_factory = Factory.create()

    @staticmethod
    def address_from_coordinates(lat, lon, id='address'):
        geocode_response = google.reverse_geocode(lat, lon)
        if not geocode_response:
            return {
                DEFAULT_VALUE_KEY: 'current location',
                'lat': lat,
                'lon': lon,
                'type': id
            }

        return {DEFAULT_VALUE_KEY: geocode_response.resolved_address,
                'lat': geocode_response.lat,
                'lon': geocode_response.lon,
                'type': id}

    @staticmethod
    def get_geocode(text, location=None, id='address'):
        geocode_response = google.geocode(text, location)
        # Reject geocode failures or non-exact responses
        if not geocode_response:
            return []

        return [
            {DEFAULT_VALUE_KEY: geocode_response.resolved_address,
             'lat': geocode_response.lat,
             'lon': geocode_response.lon,
             'type': id}
        ]

    def get_candidates(self, text, **kwargs):
        print('Resolving candidates of %s in %s' % (text, self.id))
        dialogue_state = kwargs.get('dialogue_state')
        location = get_payload_location(dialogue_state)
        if not location:
            origin = dialogue_state.get_mention('origin')
            print('origin is::', origin)
            if origin:
                location = origin.entity['lat'], origin.entity['lon']

        if text in self.local_context_resolution_triggers:
            if location:
                return [self.address_from_coordinates(location[0],
                                                      location[1], id=self.id)]
            return []
        return self.get_geocode(text, location, id=self.id)

    # Modified generate method, can now yield different address representations
    def generate(self):
        while True:
            yield str(self.fake_factory.address())


register_entity_type(AddressType())
