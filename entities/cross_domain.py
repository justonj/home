import random
from datetime import datetime

from config import config
from nlu.knowledge_base.entity_synth_helpers import SynthDataFactory
from nlu.knowledge_base.entity_type_registry import register_entity_type, \
    EntityType
from nlu.knowledge_base.entity_type_base import EntityTypeBase
from nlu.knowledge_base.entity_type_manager import generate


synth_factory = SynthDataFactory()


class CommonLocationType(EntityTypeBase):
    # yields all common location types, used for destinations/arrivals
    id = 'common_location'

    def generate(self):
        while True:
            yield None


class EmailContactType(EntityTypeBase):
    id = 'synth_emailcontact'
    name_entity_type = None
    emaildomain_entity_type = None

    def generate(self):
        if not self.name_entity_type:
            self.name_entity_type = EntityType("full_name")
        if not self.emaildomain_entity_type:
            self.emaildomain_entity_type = EntityType("email_domains")
        while True:
            name = generate(self.name_entity_type)
            if ' ' in name:
                data = name.split(" ")
            else:
                data = [name, name]
            fname = data[0].strip(".")
            lname = data[1].strip(".")
            domainname = generate(self.emaildomain_entity_type)
            if random.random() <= .4:
                yield fname + '.' + lname + '@' + domainname
            else:
                randomNumber = random.randint(0, 999)
                yield fname + '.' + lname + str(randomNumber) + '@' + domainname


class ServiceProviderType(EntityTypeBase):
    id = 'synth_email_provider'
    email_provder_name = None

    def generate(self):
        if not self.email_provder_name:
            self.email_provder_name = EntityType("email_domains")
        while True:
            provider = generate(self.email_provder_name)
            yield provider.split('.')[0]


class CityType(EntityTypeBase):
    # yields things like "Santa Monica, Chattanooga from the State/Country it belongs to"
    id = 'city_type'

    def generate(self):
        while True:
            city = synth_factory.get_geo_data('cities')
            if random.random() <= .4:
                yield city['name'] + ', ' + city['country']
            if random.random() <= .3:
                yield city['name'] + ', ' + city['region']
            else:
                yield city['name']


class StateType(EntityTypeBase):
    # yields things like "Tennessee, Bavaria from the Country it belongs to"
    id = 'state_type'

    def generate(self):
        while True:
            state = synth_factory.get_geo_data('regions')
            if random.random() <= .4:
                yield state['region'] + ', ' + state['country']
            else:
                yield state['region']


class CountryType(EntityTypeBase):
    id = 'country_type'

    def generate(self):
        while True:
            country = synth_factory.get_geo_data('countries')
            yield country


class GeneralLocationType(EntityTypeBase):
    id = 'general_location'

    def generate(self):
        while True:
            yield None


register_entity_type(CommonLocationType())
register_entity_type(CityType())
register_entity_type(StateType())
register_entity_type(GeneralLocationType())
register_entity_type(EmailContactType())
register_entity_type(ServiceProviderType())
