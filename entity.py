#!/usr/bin/env python3

import logging
import yaml

global_entities = None

class Entities:
    def __init__(self, data_file='/home/pi/entities2.yml'):
        global global_entities
        self.data_file = data_file
        self.units = {}
        self.tenants = {}
        self.import_data()
        global_entities = self

    def import_data(self):
        with open(self.data_file) as f:
            config = yaml.load(f)
        self.units = config['units']
        self.tenants = config['tenants']

    def serialize_data(self):
        data = { 'units': self.units, 'tenants': self.tenants }
        with open(self.data_file, 'w') as f:
            config = yaml.dump(data, f, default_flow_style=False)

    def synch_data(self):
        self.serialize_data()
        self.import_data()

    def print_data(self):
        for unit in self.units.values():
            print(Unit(unit))
        for tenant in self.tenants.values():
            print(Tenant(tenant))


class Entity():
    def __init__(self, data):
        self.data = data

    @property
    def paging_exception(self):
        if 'paging_exception' in self.data:
            return PagingException(self.data['paging_exception'])
        return None

    @property
    def synonyms(self):
        return [s.lower() for s in self.data['synonyms']]


class Tenant(Entity):
    default_password = 'asdfqlwevnwaevnwlvjwekfnsedhsadhfwe' # (unmatchable)

    @property
    def name(self):
        # The spoken name
        # TODO: pass in name separate because synonyms are used for speech
        # recognition, not necessarily the spoken name
        return self.data['synonyms'][0]

    @property
    def unit(self):
        return self.data['unit']

    @property
    def phone_no(self):
        if 'phone_no' in self.data:
            return self.data['phone_no']
        return ''

    @property
    def password(self):
        # must not return an empty password
        if 'password' in self.data:
            if self.data['password']:
                # it's not '' or None
                return self.data['password']
        return self.default_password

    @password.setter
    def password(self, value):
        self.data['password'] = value
        # re-write the yaml file
        global_entities.synch_data()

    @property
    def password_str(self):
        password = ''
        if self.password != self.default_password:
            password = self.password
        if password:
            retval = """
            password: %s"""%password
        else:
            retval = ''
        return retval

    def __repr__(self):
        msg = """
            name    : %s
            unit    : %s
            phone_no: %s
            synonyms: [%s]%s
"""%(self.name, self.unit, self.phone_no, ', '.join(self.synonyms),
     self.password_str)
        return msg


class Unit(Entity):
    @property
    def floor(self):
        return self.data['floor']

    @property
    def address(self):
        return self.data['synonyms'][0]

    def __repr__(self):
        return "Unit(%d, [%s])"%(self.floor, ', '.join(self.synonyms))


class PagingException:
    def __init__(self, data):
        self.data = data

    def run(self):
        if self.action:
            self.action.run()

    @property
    def message(self):
        msg = self.data['message']
        if type(msg) is not list:
            msg = [msg]
        return msg

    @property
    def action(self):
        # TODO implement
        return None
