import inspect
import re

import schemaish
from convertish import string_convert, convert


def get_converter(schema, registry, key):
    # Use the key to see if we have a specific converter
    string_key = '.'.join([str(k) for k in key])
    matching_keys = {}
    for k,v in registry.items():
        # filter out the string keys
        if isinstance(k, basestring):
            P = re.compile( '^%s$'%(k.replace('*','\w')) )
            # filter out the matching keys
            if P.match(string_key):
                matching_keys[k] = v
    if matching_keys != {}:
        keys = matching_keys.keys()
        # sort the matching keys for specificity
        keys.sort(reverse=True)
        return matching_keys[keys[0]]

    # Check the mro (adaption like check)
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
        return converter.to_type(schema, data, self, k)

    def from_type(self, schema, data, converter=None, k=None):
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

class StringConverter(Converter):
     registry = string_registry

class ScalarStringConverter(Converter):
     registry = scalar_string_registry

