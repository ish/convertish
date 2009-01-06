
About Convertish
================

Convertish is a adapting library (using peak-rules) that converts from one type of object to another. It's current implementation is wholy devoted to converting schemaish types and it implements string, dateparts, boolean and file conversion. 

How does Convertish work?
+++++++++++++++++++++++++

to convert from any schemaish type to a string, the type is passed to string_converter and the value is passed to the to_type method.. e.g.

>>> from convertish.convert import string_converter
>>> from schemaish import Integer
>>> string_converter(Integer()).from_type(1)
'1'
>>> string_converter(Integer()).to_type('1')
1
>>> 

We can do this with any schemaish type.. for instance here is a date being converted

>>> from schemaish import Date
>>> import datetime
>>> string_converter(Date()).from_type(datetime.date(2008,12,18))
'2008-12-18'
>>> string_converter(Date()).to_type('2008-12-18')
datetime.date(2008, 12, 18)

This is used in formish's widgets to serialise objects.


The Convert Module
++++++++++++++++++

Validate implements the following validators.. 


.. autoclass:: convertish.convert.NumberToStringConverter
.. autoclass:: convertish.convert.IntegerToStringConverter
.. autoclass:: convertish.convert.FloatToStringConverter
.. autoclass:: convertish.convert.BooleanToStringConverter
.. autoclass:: convertish.convert.DateToStringConverter
.. autoclass:: convertish.convert.TimeToStringConverter
.. autoclass:: convertish.convert.FileToStringConverter
.. autoclass:: convertish.convert.SequenceToStringConverter
.. autoclass:: convertish.convert.TupleToStringConverter


.. autoclass:: convertish.convert.DateToDateTupleConverter
