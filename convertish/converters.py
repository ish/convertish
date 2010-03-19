
import inspect
import re

import schemaish
from convertish import string_convert, convert
from dottedish import api


def container_factory(parent_key, item_key):
    return {}




def get_converter(schema, registry, key):
    string_key = '.'.join([str(k) for k in key])
    print 'KEY', string_key
    print 'REG',registry
    matching_keys = {}
    for k,v in registry.items():
        if isinstance(k, basestring):
            P = re.compile( '^%s$'%(k.replace('*','\w')) )
            print 'k',k
            print 'P',P.match(string_key)
        if isinstance(k, basestring) and P.match(string_key):
            matching_keys[k] = v
    print 'MK',matching_keys
    if matching_keys != {}:
        keys = matching_keys.keys()
        keys.sort(reverse=True)
        return matching_keys[keys[0]]

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
        if k is None:
            k = []
        converter = get_converter(schema, self.registry, k)
        print 'CONVER',converter
        return converter.to_type(schema, data, self, k)

    def from_type(self, schema, data, converter=None, k=None):
        if k is None:
            k = []
        converter = get_converter(schema, self.registry, k)
        print 'CONVER',converter
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

class StringConverter(Converter):
     registry = string_registry

class ScalarStringConverter(Converter):
     registry = scalar_string_registry

#json_converter = Converter({
#    schemaish.Integer: string_convert.IntegerToStringConverter(),
#})

