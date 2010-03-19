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

The converters don't just handle 'leaf' nodes, they should also handle nodes with children too.. e.g. 

.. code-block:: python

    class SequenceNullConverter(BaseConverter):

        def from_type(self, schema, data, converter, key):
            out = []
            child_schema_type = schema.attr
            for n, value in enumerate(data):
                new_key = key+[n]
                new_value = converter.from_type(child_schema_type, value, converter, new_key)
                out.append(new_value)
            return out

        def to_type(self, schema, data, converter, k):
            out = []
            child_schema_type = schema.attr
            for n, value in enumerate(data):
                new_key = key+[n]
                new_value = converter.to_type(child_schema_type, value, converter, new_key)
                out.append(new_value)
            return out


The above converter leaves any sequences alone but calls the converters on each of the sequences items.

A converter should call out to handle any of it's children (apart from very special cases). You can see tha the key is being appended to each time the sub converter is called.

A full registry
---------------

Here is a full registry which converts all leaf nodes to strings but leaves structures, sequences and tuples alone.

.. code-block:: python

    scalar_string_registry = {
        schemaish.String:    convert.NullConverter(),
        schemaish.Integer:   string_convert.IntegerToStringConverter(),
        schemaish.Float:     string_convert.FloatToStringConverter(),
        schemaish.Boolean:   string_convert.BooleanToStringConverter(),
        schemaish.Date:      string_convert.DateToStringConverter(),
        schemaish.DateTime:  string_convert.DateTimeToStringConverter(),
        schemaish.Time:      string_convert.TimeToStringConverter(),
        schemaish.File:      string_convert.FileToStringConverter(),
        schemaish.Sequence:  string_convert.SequenceNullConverter(),
        schemaish.Tuple:     string_convert.TupleNullConverter(),
        schemaish.Structure: string_convert.StructureNullConverter(),
    }

We create a Converter from this registry as follows

.. code-block:: python

    class ScalarStringConverter(Converter):
        registry = scalar_string_registry

For most uses, these types of 'adapter' style registrys are adequate. However, in some cases you might wish to change the way adapters work for particular keys or patterns. In order to do this, you can use a string as a key in the registry and this string will be used as a pattern matcher for the key at the point of conversion. The following ini style converter demonstrates the need for this pattern of use. 

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

Where the StringConverter will convert everything it gets into a string serialisation, sequences turned into csv style lists for instance, this ini file registry uses the scalar_string_registry as a base. (as ssen previously in the full registry section). The registry is then specialised by serialising everything two levels deep and below as strings and also passing any top level structure types to an INIConverter. 

The INIConverter uses ConfigParser to do it's final serialisation as follows

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



YAML reader
-----------

If you use yaml without implicit type conversion you will receive your data back from the yaml load as a structure of strings (lists of strings and dictionaries of strings). Using the convertish and schemaish modules will allow you to load a yaml file according to a schema. 

.. code-block:: python

    class StructureYAMLConverter(BaseConverter):

        def from_type(self, schema, data, converter, k):
            out = {}
            for n,attr in schema.attrs:
                out[n] = converter.from_type(attr, data[n], converter, k=k+[n])
            return yaml.dump(out)

        def to_type(self, schema, data, converter, k):
            d = yaml.load(data)
            out = {}
            for n, attr in schema.attrs:
                out[n] = converter.to_type(attr, d[n], converter, k=k+[n])
            return out

    yaml_registry = {
        schemaish.Structure: string_convert.StructureYAMLConverter(),
        '*': ScalarStringConverter(),
    }

    class YAMLConverter(Converter):
         registry = yaml_registry


This only copes with structures at the top level of a yaml document, the actual code includes a registry entry to sequences also. To use this, you would do the following


.. doctest::

    >>> import convertish, schemaish
    >>> schema = schemaish.Structure()
    >>> schema.add('a', schemaish.Integer())
    >>> data = {'a': 7}
    >>> from convertish.converters import YAMLConverter
    >>> YAMLConverter().from_type(schema, data)
    "{b: '7'}\n"
    >>> YAMLConverter().to_type(schema, "{b: '7'}\n")
    {'b': 7}

Setting up new converters is as simple as creating a new registry dictionary.
