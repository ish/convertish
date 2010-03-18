
import inspect

import schemaish
from convertish import string_convert, convert

# example converter registry


def get_converter(schema, registry):
    print 'int get convert'
    for t in inspect.getmro(type(schema))[:-1]:
        if t in registry:
            return registry[t]
    raise NotImplementedError

_registry = {
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

class Converter(object):

    registry = _registry

    def __init__(self, **kw):
        self.registry = dict(self.registry)
        self.registry.update(kw.get('registry',{}))
        self.converter_options = kw.pop('converter_options', {})
        # walk up MRO to see if we have a converter

    def to_type(self, schema, data, converter=None):
        converter = get_converter(schema, self.registry)
        return converter.to_type(schema, data, converter=self)

    def from_type(self, schema, data, converter=None):
        converter = get_converter(schema, self.registry)
        return converter.from_type(schema, data, converter=self)


#json_converter = Converter({
#    schemaish.Integer: string_convert.IntegerToStringConverter(),
#})

