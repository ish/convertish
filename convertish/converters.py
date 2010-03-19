import inspect
import re

import schemaish
from convertish import string_convert, convert, json_convert, ini_convert

import logging
log = logging.getLogger(__name__)


def get_converter(schema, registry, key):
    # Use the key to see if we have a specific converter
    string_key = '.'.join([str(k) for k in key])
    matching_keys = {}
    for k,v in registry.items():
        # filter out the string keys
        if isinstance(k, basestring):
            log.info('string_key: %s'%string_key)
            log.info('%s is string matcher'%(k,))
            log.info('regexp is %s'%'^%s'%(k.replace('*','\w+')))
            P = re.compile( '^%s'%(k.replace('*','\w+')) )
            # filter out the matching keys
            if P.match(string_key):
                log.info('string_key: %s matches: %s'%(string_key,k))
                matching_keys[k] = v
    log.info( 'matching keys %s'%matching_keys)
    if matching_keys != {}:
        keys = matching_keys.keys()
        # sort the matching keys for specificity
        keys.sort(reverse=True)
        return matching_keys[keys[0]]

    log.info('adapting instead')
    # Check the mro (adaption like check)
    log.info('schema %s'%schema)
    for t in inspect.getmro(type(schema))[:-1]:
        if t in registry:
            return registry[t]
    raise NotImplementedError

class Converter(object):

    registry = {}

    def __init__(self, **kw):
        self.registry = dict(self.registry)
        self.registry.update(kw.get('registry',{}))
        self.converter_options = kw.pop('converter_options', {})

    def to_type(self, schema, data, converter=None, k=None):
        log.info('got k %s'%k)
        if k is None:
            k = []
        converter = get_converter(schema, self.registry, k)
        return converter.to_type(schema, data, self, k)

    def from_type(self, schema, data, converter=None, k=None):
        log.info( 'got k %s'%k)
        if k is None:
            k = []
        converter = get_converter(schema, self.registry, k)
        return converter.from_type(schema, data, self, k)

scalar_string_registry = {
  schemaish.Integer: string_convert.IntegerToStringConverter(),
  schemaish.String: convert.NullConverter(),
  schemaish.Float: string_convert.FloatToStringConverter(),
  schemaish.Date: string_convert.DateToStringConverter(),
  schemaish.Boolean: string_convert.BooleanToStringConverter(),
  schemaish.File: string_convert.FileToStringConverter(),
  schemaish.DateTime: string_convert.DateTimeToStringConverter(),
  schemaish.Sequence: string_convert.SequenceNullConverter(),
  schemaish.Time: string_convert.TimeToStringConverter(),
  schemaish.Tuple: string_convert.TupleNullConverter(),
}

string_registry = {
  schemaish.Integer: string_convert.IntegerToStringConverter(),
  schemaish.String: convert.NullConverter(),
  schemaish.Float: string_convert.FloatToStringConverter(),
  schemaish.Date: string_convert.DateToStringConverter(),
  schemaish.Boolean: string_convert.BooleanToStringConverter(),
  schemaish.File: string_convert.FileToStringConverter(),
  schemaish.DateTime: string_convert.DateTimeToStringConverter(),
  schemaish.Sequence: string_convert.SequenceToStringConverter(),
  schemaish.Time: string_convert.TimeToStringConverter(),
  schemaish.Tuple: string_convert.TupleToStringConverter(),
}

json_structure_registry = {
    schemaish.Integer: convert.NullConverter(),
    schemaish.String: convert.NullConverter(),
    schemaish.Float: convert.NullConverter(),
    schemaish.Boolean: convert.NullConverter(),
    schemaish.File: string_convert.FileToStringConverter(),
    schemaish.Sequence: string_convert.SequenceNullConverter(),
    schemaish.Tuple: string_convert.TupleNullConverter(),
    schemaish.Date: json_convert.DateToJSONConverter(),
    schemaish.Time: json_convert.TimeToJSONConverter(),
}


class StringConverter(Converter):
     registry = string_registry

class ScalarStringConverter(Converter):
     registry = scalar_string_registry

class JSONStructureConverter(Converter):
     registry = json_structure_registry

ini_registry = dict(scalar_string_registry)
ini_registry.update({
    schemaish.Structure: string_convert.StructureINIConverter(),
    '*.*': StringConverter(),
})

class INIConverter(Converter):
     registry = ini_registry
