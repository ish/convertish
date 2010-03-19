************
* Convertish
************


Convertish serialisation tools
==============================

Basic Conversion
----------------

A convertish converter uses a dictionary register in order to work out how to
serialise any object. Convertish also supplies a set of converters and
registries for many common purposes. 

To explain how convertish works, we'll take a look at some simple conversions. 

.. doctest::

    >>> import convertish, schemaish
    >>> schema = schemaish.Boolean()
    >>> data = True
    >>> from convertish.converters import StringConverter
    >>> StringConverter().from_type(schema, data)
    'True'

If we look at the StringConverter module, we can see how it is set up... 



.. code-block:: python

    class Converter(object):

        registry = {}

        def __init__(self, **kw):
            self.registry = dict(self.registry)
            self.registry.update(kw.get('registry',{}))

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

The Converter class has a base registry and can be instantiated with another
registry which updates the bae one. from_type is called along with the schema
and the actual data. You can see that the converter itself takes a converter
and also 'k' (the list of keys to get to the currently processed data**). 

** k, which is a list of the keys for the data currently being processed, (e.g.
['a','x']) is a bit of context so that the converter registry can provide
converters depending on how deep into a data structure we are - e.g. for a
config ini converter, anything below 2 levels down should be string
serialised.. possibly.

The first thing that happens is that 'get_converter' is called with the current
schema, the registry and the current key. Lets have a quick look at an example
registry.

.. code-block:: python

    scalar_string_registry = {
      schemaish.Integer: string_convert.IntegerToStringConverter(),
      schemaish.String: convert.NullConverter(),
      schemaish.Float: string_convert.FloatToStringConverter(),
      schemaish.Date: string_convert.DateToStringConverter(),
      schemaish.Boolean: string_convert.BooleanToStringConverter(),
    }

A basic registry just lists the schema types and what converter should be used to convert them. The individual converters just implement a from_type and to_type themselves. The following is a slightly simplified version of the BooleanToStringConverter (which doesn't implement the None type checking).

.. code-block:: python
    class BooleanToStringConverter(BaseConverter):

        def from_type(self, schema, data, converter, k):
            if data:
                return 'True'
            return 'False'

        def to_type(self, schema, data, converter, k):
            data = data.strip()
            if data not in ('True', 'False'):
                raise ConvertError('%r should be either True or False'%data)
            return data == 'True'

The converters don't just handle 'leaf' nodes, they should also handle parents too.. e.g. 

.. code-block:: python

    class SequenceNullConverter(BaseConverter):

        def from_type(self, schema, data, converter, k):
            return [converter.from_type(schema.attr, item, converter, k=k+[n]) for
                    n, item in enumerate(data)]

        def to_type(self, schema, data, converter, k):
            return [converter.to_type(schema.attr, item, converter, k=k+[n]) for
                    n, item in enumerate(data)]

The above converter leaves any sequences along but calls the converters on each of the sequences items.

A converter should call out to handle any of it's children (apart from very special cases). You can see tha the key is being appended to each time the sub converter is called.

A full registry
---------------

Here is a full registry which converts all leaf nodes to strings but leaves structures, sequences and tuples alone.

.. code-block:: python

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

We create a Converter from this registry as follows

.. code-block:: python

    class ScalarStringConverter(Converter):
        registry = scalar_string_registry

For most uses, these types of 'adapter' style registrys are more than enough. However, in some cases you might wish to change the way adapters work for particular keys or patterns. In order to do this, you can use a string as a key in the registry and this string will be used as a pattern match for the key at the point of conversion. 

An 'ini' converter
------------------

For example, if we wanted to convert a set of values into a config parser style string, the following is used for the registry.

.. code-block:: python
 
    ini_registry = dict(scalar_string_registry)
    ini_registry.update({
        schemaish.Structure: string_convert.StructureINIConverter(),
        '*.*': StringConverter(),
    })

    class INIConverter(Converter):
         registry = ini_registry

Where the StringConverter will convert everything it gets into a string serialisation. This ini file uses the scalar string registry as a base and then specialises it by serialising everything below two levels deep as strings and also passing any top level structures to an INIConverter. 

The INIConverter uses ConfigParser as follows..

.. code-block:: python

    class StructureINIConverter(BaseConverter):

        def from_type(self, schema, data, converter, k):
            config = ConfigParser.RawConfigParser()
            for K,attr in schema.attrs:
                config.add_section(K)
                for k, a in attr.attrs:
                    config.set(K,k,data[K][k])
            f = StringIO()
            config.write(f)
            f.seek(0,0)
            return f.read()


