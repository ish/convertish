
import inspect

import schemaish
from convertish import string_convert, convert
from dottedish import api

# example converter registry


def container_factory(parent_key, item_key):
    return {}

def expand_registry(registry):
    for k, v in registry.items():
        if isinstance(k, basestring):
            api.set(registry, k, v, container_factory=container_factory)
            if '.' in k:
                del registry[k]
    return registry



def get_converter(schema, registry, key):
    #print '*'*80
    #print 'K going in',key
    #print 'Registry going in ',registry

    R = expand_registry(registry)
    #print 'R',R
    Rsub = dict(R)
    for n in key:
        k = str(n)
        #print 'k',k
        #print 'Rsub',Rsub
        try:
            if k in Rsub:
                #print 'k was in rsub'
                Rsub = Rsub[k]
                #print 'RSUB now',Rsub
                continue
            elif '*' in Rsub:
                Rsub = Rsub['*']
                continue
        except TypeError:
            return Rsub
        #print 'before break'
        break
    else:
        #print 'in else'
        if not hasattr(Rsub,'keys'):
            return Rsub

    #print 'adapting'
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
        # walk up MRO to see if we have a converter

    def to_type(self, schema, data, converter=None, k=None):
        #print 'called with k=',k
        if k is None:
            k = []
        converter = get_converter(schema, self.registry, k)
        return converter.to_type(schema, data, self, k)

    def from_type(self, schema, data, converter=None, k=None):
        #print 'called with k=',k
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
  schemaish.Sequence: string_convert.SequenceToStringConverter(),
  schemaish.Time: string_convert.TimeToStringConverter(),
  schemaish.Tuple: string_convert.TupleToStringConverter(),
}


class ScalarStringConverter(Converter):
     registry = scalar_string_registry

#json_converter = Converter({
#    schemaish.Integer: string_convert.IntegerToStringConverter(),
#})

