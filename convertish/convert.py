__all__ = ['string_converter', 'datetuple_converter', 'boolean_converter',
           'file_converter','json_converter']

import csv
from cStringIO import StringIO
from datetime import date, time
from simplegeneric import generic
import schemaish

try:
    import decimal
    haveDecimal = True
except ImportError:
    haveDecimal = False


class ConvertError(Exception):
    """
    Exception to indicate failure in converting values.
    """

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

    def __str__(self):
        return self.message
    __unicode__ = __str__

    # Hide Python 2.6 deprecation warnings.
    def _get_message(self): return self._message
    def _set_message(self, message): self._message = message
    message = property(_get_message, _set_message)


class Converter(object):
    
    def __init__(self, schema_type, **k):
        self.schema_type = schema_type
        self.converter_options = k.pop('converter_options', {})
        
    def from_type(self, value, converter_options={}):
        """
        convert from i.e. for NumberToString converter - from number to string
        """
    
    def to_type(self, value, converter_options={}):
        """
        convert to i.e. for NumberToString converter - to number from string
        """


class NullConverter(Converter):

    def from_type(self, value, converter_options={}):
        return value
    
    def to_type(self, value, converter_options={}):
        return value


class NumberToStringConverter(Converter):

    cast = None
    type_string = 'number'
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return str(value)
    
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        # "Cast" the value to the correct type. For some strange reason,
        # Python's decimal.Decimal type raises an ArithmeticError when it's
        # given a dodgy value.
        value = value.strip()
        try:
            value = self.cast(value)
        except (ValueError, ArithmeticError):
            raise ConvertError("Not a valid %s"%self.type_string)
        return value
        
        
class IntegerToStringConverter(NumberToStringConverter):
    cast = int
    type_string = 'integer'


class FloatToStringConverter(NumberToStringConverter):
    cast = float


if haveDecimal:
    class DecimalToStringConverter(NumberToStringConverter):
        cast = decimal.Decimal


class FileToStringConverter(Converter):
    """
    Convert between a text File and a string.

    The file's content is assumed to be a UTF-8 encoded string. Anything else
    will almost certainly break the code and/or page.

    Converting from a string to a File instance returns a new File with a
    default name, content.txt, of type text/plain.
    """
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        if not value.file:
            raise ValueError('Cannot convert to string without a file-like '
                             'object to read from')
        return value.file.read().decode('utf-8')
        
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
        return schemaish.type.File(StringIO(value.encode('utf-8')),
                                   'content.txt', 'text/plain')

    
class BooleanToStringConverter(Converter):
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        if value:
            return 'True'
        return 'False'
        
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
        if value not in ('True', 'False'):
            raise ConvertError('%r should be either True or False'%value)
        return value == 'True'

    
class DateToStringConverter(Converter):
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return value.isoformat()
    
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
        return self.parseDate(value)
        
    def parseDate(self, value):
        try:
            y, m, d = [int(p) for p in value.split('-')]
        except ValueError:
            raise ConvertError('Invalid date')
        try:
            value = date(y, m, d)
        except ValueError, e:
            raise ConvertError('Invalid date: '+str(e))
        return value


class TimeToStringConverter(Converter):
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return value.isoformat()
    
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
        return self.parseTime(value)
        
    def parseTime(self, value):
        
        if '.' in value:
            value, ms = value.split('.')
        else:
            ms = 0
            
        try:
            parts = value.split(':')  
            if len(parts)<2 or len(parts)>3:
                raise ValueError()
            if len(parts) == 2:
                h, m = parts
                s = 0
            else:
                h, m, s = parts
            h, m, s, ms = int(h), int(m), int(s), int(ms)
        except:
            raise ConvertError('Invalid time')
        
        try:
            value = time(h, m, s, ms)
        except ValueError, e:
            raise ConvertError('Invalid time: '+str(e))
            
        return value

    
class DateToDateTupleConverter(Converter):
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return value.year, value.month, value.day
        
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        try:
            try:
                V = [int(v) for v in value]
            except ValueError:
                raise ConvertError('Invalid Number')
            value = date(*V)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid date: '+str(e))
        return value


def getDialect(delimiter=','):
    class Dialect(csv.excel):
        def __init__(self, *a, **k):
            self.delimiter = k.pop('delimiter',',')
            csv.excel.__init__(self,*a, **k)
    return Dialect(delimiter=delimiter)


def convert_csvrow_to_list(row, delimiter=','):
    dialect = getDialect(delimiter=delimiter)
    sf = StringIO()
    csvReader = csv.reader(sf, dialect=dialect)
    sf.write(row)
    sf.seek(0,0)
    return csvReader.next()

    
def convert_list_to_csvrow(l, delimiter=','):
    dialect = getDialect(delimiter=delimiter)
    sf = StringIO()
    writer = csv.writer(sf, dialect=dialect)
    writer.writerow(l)
    sf.seek(0,0)
    return sf.read().strip()

        
class SequenceToStringConverter(Converter):
    """
    I'd really like to have the converter options on the init but ruledispatch
    won't let me pass keyword arguments
    """
    
    def __init__(self, schema_type, **k):
        Converter.__init__(self, schema_type, **k)
        
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        delimiter = converter_options.get('delimiter',',')
        if isinstance(self.schema_type.attr, schemaish.Sequence):
            out = []
            for line in value:
                lineitems =  [
                  string_converter(self.schema_type.attr.attr).from_type(item) \
                    for item in line]
                linestring = convert_list_to_csvrow( \
                    lineitems, delimiter=delimiter)
                out.append(linestring)
            return '\n'.join(out)
        elif isinstance(self.schema_type.attr, schemaish.Tuple):
            out = []
            for line in value:
                lineitems =  [
              string_converter(self.schema_type.attr.attrs[n]).from_type(item) \
                    for n,item in enumerate(line) ]
                linestring = convert_list_to_csvrow( \
                    lineitems, delimiter=delimiter)
                out.append(linestring)
            return '\n'.join(out)
 
        else:
            value =  [string_converter(self.schema_type.attr).from_type(v) \
                      for v in value]
            return convert_list_to_csvrow(value, delimiter=delimiter)
    
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
        delimiter = converter_options.get('delimiter',',')
        if isinstance(self.schema_type.attr, schemaish.Sequence):
            out = []
            for line in value.split('\n'):
                l = convert_csvrow_to_list(line, delimiter=delimiter)
                convl = [
                 string_converter(self.schema_type.attr.attr).to_type(v) \
                         for v in l]
                out.append( convl )
            return out
        if isinstance(self.schema_type.attr, schemaish.Tuple):
            out = []
            for line in value.split('\n'):
                l = convert_csvrow_to_list(line, delimiter=delimiter)
                convl = [string_converter(self.schema_type.attr.attrs[n]).to_type(v) \
                         for n,v in enumerate(l)]
                out.append( tuple(convl) )
            return out
        else:
            if delimiter != '\n' and len(value.split('\n')) > 1:
                raise ConvertError("More than one line found" \
                           " for csv with delimiter=\'%s\'"%delimiter)
            if delimiter == '\n':
                out = value.splitlines()
            else:
                out = convert_csvrow_to_list(value, delimiter=delimiter)
                
            return [string_converter(self.schema_type.attr).to_type(v) \
                    for v in out]


class TupleToStringConverter(Converter):
    """
    Convert a tuple to and from a string.

    XXX tim: I'd really like to have the converter options on the init but ruledispatch
    won't let me pass keyword arguments
    XXX matt: the default to_type items should be configurable but None is
    better than '' because it doesn't crash the item's converter ;-).
    """
    
    def __init__(self, schema_type, **k):
        Converter.__init__(self, schema_type, **k)
        
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        delimiter = converter_options.get('delimiter',',')
        lineitems =  [string_converter(self.schema_type.attrs[n]).from_type(item) \
                      for n,item in enumerate(value)]
        return convert_list_to_csvrow(lineitems, delimiter=delimiter)
    
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
        delimiter = converter_options.get('delimiter',',')
        l = convert_csvrow_to_list(value, delimiter=delimiter)
        if len(l) > len(self.schema_type.attrs):
            raise ConvertError('Too many arguments')
        if len(l) < len(self.schema_type.attrs):
            raise ConvertError('Too few arguments')
        def convert_or_none(n, v):
            v = v.strip()
            if not v:
                return None
            return string_converter(self.schema_type.attrs[n]).to_type(v)
        return tuple(convert_or_none(n, v) for (n, v) in enumerate(l))


class TupleToListConverter(Converter):

    def __init__(self, schema_type, **k):
        Converter.__init__(self, schema_type, **k)

    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return list(value)

    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        return tuple(value)


####
#
#  String Converter
    
@generic
def string_converter(schema_type):
    pass

@string_converter.when_type(schemaish.String)
def string_to_string(schema_type):
    return NullConverter(schema_type)

@string_converter.when_type(schemaish.Integer)
def int_to_string(schema_type):
    return IntegerToStringConverter(schema_type)

@string_converter.when_type(schemaish.Float)
def float_to_string(schema_type):
    return FloatToStringConverter(schema_type)

@string_converter.when_type(schemaish.Decimal)
def decimal_to_string(schema_type):
    return DecimalToStringConverter(schema_type)

@string_converter.when_type(schemaish.Date)
def date_to_string(schema_type):
    return DateToStringConverter(schema_type)

@string_converter.when_type(schemaish.Time)
def time_to_string(schema_type):
    return TimeToStringConverter(schema_type)

@string_converter.when_type(schemaish.Sequence)
def sequence_to_string(schema_type):
    return SequenceToStringConverter(schema_type)

@string_converter.when_type(schemaish.Tuple)
def tuple_to_string(schema_type):
    return TupleToStringConverter(schema_type)

@string_converter.when_type(schemaish.Boolean)
def boolean_to_string(schema_type):
    return BooleanToStringConverter(schema_type)

@string_converter.when_type(schemaish.File)
def file_to_string(schema_type):
    return FileToStringConverter(schema_type)


####
#
#  Date Tuple Converter

@generic
def datetuple_converter(schema_type):
    pass

@datetuple_converter.when_type(schemaish.Date)
def date_to_datetuple(schema_type):
    return DateToDateTupleConverter(schema_type)


####
#
#  Boolean Converter

@generic
def boolean_converter(schema_type):
    pass

@boolean_converter.when_type(schemaish.Boolean)
def boolean_to_boolean(schema_type):
    return NullConverter(schema_type)

@generic
def file_converter(schema_type):
    pass

@file_converter.when_type(schemaish.File)
def file_to_file(schema_type):
    return NullConverter(schema_type)


####
#
#  JSON Converter


class DateToJSONConverter(Converter):
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return {'__type__':'date','year':value.year, 'month':value.month, 'day':value.day}
        
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        try:
            try:
                year, month, day = int(value['year']) ,int(value['month']) ,int(value['day']) ,
            except ValueError:
                raise ConvertError('Invalid Number')
            value = date(year, month, day)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid date: '+str(e))
        return value


class TimeToJSONConverter(Converter):
    
    def from_type(self, value, converter_options={}):
        if value is None:
            return None
        return {'__type__':'time','hour':value.hour, 'minute':value.minute, 'second':value.second,'microsecond':value.microsecond}
        
    def to_type(self, value, converter_options={}):
        if value is None:
            return None
        try:
            try:
                h, m, s, ms = int(value['hour']), int(value['minute']), int(value['second']) ,int(value.get('microsecond',0))
            except ValueError:
                raise ConvertError('Invalid Number')
            value = time(h, m, s, ms)
        except (TypeError, ValueError), e:
            raise ConvertError('Invalid time: '+str(e))
        return value


@generic
def json_converter(schema_type):
    pass

@json_converter.when_type(schemaish.String)
def string_to_json(schema_type):
    return NullConverter(schema_type)

@json_converter.when_type(schemaish.Integer)
def int_to_json(schema_type):
    return NullConverter(schema_type)

@json_converter.when_type(schemaish.Float)
def float_to_json(schema_type):
    return NullConverter(schema_type)

# XXX
@json_converter.when_type(schemaish.Decimal)
def decimal_to_json(schema_type):
    return NullConverter(schema_type)

@json_converter.when_type(schemaish.Date)
def date_to_json(schema_type):
    return DateToJSONConverter(schema_type)

@json_converter.when_type(schemaish.Time)
def time_to_json(schema_type):
    return TimeToJSONConverter(schema_type)

@json_converter.when_type(schemaish.Sequence)
def sequence_to_json(schema_type):
    return NullConverter(schema_type)

@json_converter.when_type(schemaish.Tuple)
def tuple_to_json(schema_type):
    return TupleToListConverter(schema_type)

@json_converter.when_type(schemaish.Boolean)
def boolean_to_json(schema_type):
    return NullConverter(schema_type)

@json_converter.when_type(schemaish.File)
def file_to_json(schema_type):
    return FileToStringConverter(schema_type)

