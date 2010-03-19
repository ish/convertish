import csv
from cStringIO import StringIO
from datetime import date, datetime, time
import schemaish

try:
    import decimal
    haveDecimal = True
except ImportError:
    haveDecimal = False

from convertish.convert import BaseConverter, ConvertError
from convertish.util import SimpleTZInfo


class NumberToStringConverter(BaseConverter):

    cast = None
    type_string = 'number'

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        return str(data)

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        # "Cast" the data to the correct type. For some strange reason,
        # Python's decimal.Decimal type raises an ArithmeticError when it's
        # given a dodgy data.
        data = data.strip()
        try:
            data = self.cast(data)
        except (ValueError, ArithmeticError):
            raise ConvertError("Not a valid %s"%self.type_string)
        return data


class IntegerToStringConverter(NumberToStringConverter):
    cast = int
    type_string = 'integer'


class FloatToStringConverter(NumberToStringConverter):
    cast = float


if haveDecimal:
    class DecimalToStringConverter(NumberToStringConverter):
        cast = decimal.Decimal


class FileToStringConverter(BaseConverter):
    """
    Convert between a text File and a string.

    The file's content is assumed to be a UTF-8 encoded string. Anything else
    will almost certainly break the code and/or page.

    Converting from a string to a File instance returns a new File with a
    default name, content.txt, of type text/plain.
    """

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        if not data.file:
            raise ValueError('Cannot convert to string without a file-like '
                             'object to read from')
        return data.file.read().decode('utf-8')

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        data = data.strip()
        return schemaish.type.File(StringIO(data.encode('utf-8')),
                                   'content.txt', 'text/plain')


class BooleanToStringConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        if data:
            return 'True'
        return 'False'

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        data = data.strip()
        if data not in ('True', 'False'):
            raise ConvertError('%r should be either True or False'%data)
        return data == 'True'


def _parse_date(data):
    try:
        y, m, d = [int(p) for p in data.split('-')]
    except ValueError:
        raise ConvertError('Invalid date')
    try:
        data = date(y, m, d)
    except ValueError, e:
        raise ConvertError('Invalid date: '+str(e))
    return data


def _parse_time(data):

    # Parse the timezone offset
    if '+' in data:
        data, tz = data.split('+')
        tzdir = 1
    elif '-' in data:
        data, tz = data.split('-')
        tzdir = -1
    else:
        tz = None
    if tz:
        hours, minutes = tz.split(':')
        tz = SimpleTZInfo(tzdir*((int(hours)*60) + int(minutes)))

    # Parse milliseconds.
    if '.' in data:
        data, ms = data.split('.')
    else:
        ms = 0

    # Parse hours, minutes and seconds.
    try:
        parts = data.split(':')
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
        data = time(h, m, s, ms, tz)
    except ValueError, e:
        raise ConvertError('Invalid time: '+str(e))

    return data


class DateToStringConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        return data.isoformat()

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        data = data.strip()
        return _parse_date(data)


class TimeToStringConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        return data.isoformat()

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        data = data.strip()
        return _parse_time(data)


class DateTimeToStringConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        return data.isoformat()

    def to_type(self, schema, data, converter, k):
        d, t = data.split('T')
        d = _parse_date(d)
        t = _parse_time(t)
        return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second,
                        t.microsecond, t.tzinfo)


def getDialect(delimiter=','):
    class Dialect(csv.excel):
        def __init__(self, *a, **k):
            self.delimiter = k.pop('delimiter',',')
            csv.excel.__init__(self,*a, **k)
    return Dialect(delimiter=delimiter)


def convert_csvrow_to_list(row, delimiter=','):
    sf = StringIO()
    sf.write(row.encode('utf-8'))
    sf.seek(0,0)
    reader = csv.reader(sf, dialect=getDialect(delimiter=delimiter))
    return list(_decode_row(reader.next()))


def convert_list_to_csvrow(l, delimiter=','):
    sf = StringIO()
    writer = csv.writer(sf, dialect=getDialect(delimiter=delimiter))
    writer.writerow(list(_encode_row(l)))
    sf.seek(0,0)
    return sf.read().strip().decode('utf-8')


def _encode_row(row, encoding='utf-8'):
    for cell in row:
        if cell is not None:
            cell = cell.encode(encoding)
        yield cell


def _decode_row(row, encoding='utf-8'):
    for cell in row:
        yield cell.decode(encoding)


class SequenceToStringConverter(BaseConverter):
    """
    I'd really like to have the converter options on the init but ruledispatch
    won't let me pass keyword arguments
    """

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        delimiter = self.converter_options.get('delimiter',',')
        if isinstance(schema.attr, schemaish.Sequence):
            out = []
            for n,line in enumerate(data):
                lineitems =  [
                  converter.from_type(schema.attr.attr, item, converter, k=k+[n]) \
                    for item in line]
                linestring = convert_list_to_csvrow( \
                    lineitems, delimiter=delimiter)
                out.append(linestring)
            return '\n'.join(out)
        elif isinstance(schema.attr, schemaish.Tuple):
            out = []
            for n, line in enumerate(data):
                lineitems =  [
              converter.from_type(schema.attr.attrs[n], item, converter, k=k+[n]) \
                    for n,item in enumerate(line) ]
                linestring = convert_list_to_csvrow( \
                    lineitems, delimiter=delimiter)
                out.append(linestring)
            return '\n'.join(out)

        else:
            data =  [converter.from_type(schema.attr, v, converter, k=k+[n]) \
                      for n, v in enumerate(data)]
            return convert_list_to_csvrow(data, delimiter=delimiter)

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        data = data.strip()
        delimiter = self.converter_options.get('delimiter',',')
        if isinstance(schema.attr, schemaish.Sequence):
            out = []
            for line in data.split('\n'):
                l = convert_csvrow_to_list(line, delimiter=delimiter)
                convl = [
                 converter.to_type(schema.attr.attr, v, converter, k=k+[n]) \
                         for n, v in enumerate(l)]
                out.append( convl )
            return out
        if isinstance(schema.attr, schemaish.Tuple):
            out = []
            for line in data.split('\n'):
                l = convert_csvrow_to_list(line, delimiter=delimiter)
                convl = [converter.to_type(schema.attr.attrs[n], v, converter,
                                          k=k+[n]) for n,v in enumerate(l)]
                out.append( tuple(convl) )
            return out
        else:
            if delimiter != '\n' and len(data.split('\n')) > 1:
                raise ConvertError("More than one line found" \
                           " for csv with delimiter=\'%s\'"%delimiter)
            if delimiter == '\n':
                out = data.splitlines()
            else:
                out = convert_csvrow_to_list(data, delimiter=delimiter)

            return [converter.to_type(schema.attr, v, converter, k=k+[n]) \
                    for n, v in enumerate(out)]


class TupleToStringConverter(BaseConverter):
    """
    Convert a tuple to and from a string.

    XXX tim: I'd really like to have the converter options on the init but ruledispatch
    won't let me pass keyword arguments
    XXX matt: the default to_type items should be configurable but None is
    better than '' because it doesn't crash the item's converter ;-).
    """

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        delimiter = self.converter_options.get('delimiter',',')
        lineitems =  [converter.from_type(schema.attrs[n], item, converter,
                                          k=k+[n]) \
                      for n,item in enumerate(data)]
        return convert_list_to_csvrow(lineitems, delimiter=delimiter)

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        data = data.strip()
        delimiter = self.converter_options.get('delimiter',',')
        l = convert_csvrow_to_list(data, delimiter=delimiter)
        if len(l) > len(schema.attrs):
            raise ConvertError('Too many arguments')
        if len(l) < len(schema.attrs):
            raise ConvertError('Too few arguments')
        def convert_or_none(n, v):
            v = v.strip()
            if not v:
                return None
            return converter.to_type(schema.attrs[n], v, converter, k=k+[n])
        return tuple(convert_or_none(n, v) for (n, v) in enumerate(l))



class SequenceNullConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        return [converter.from_type(schema.attr, item, converter, k=k+[n]) for
                n, item in enumerate(data)]

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        return [converter.to_type(schema.attr, item, converter, k=k+[n]) for
                n, item in enumerate(data)]


class TupleNullConverter(BaseConverter):

    def from_type(self, schema, data, converter, k):
        if data is None:
            return None
        return tuple([converter.from_type(schema.attrs[n], item, converter,
                                          k=k+[n]) for n,
    item in enumerate(data)])

    def to_type(self, schema, data, converter, k):
        if data is None:
            return None
        return tuple([converter.to_type(schema.attrs[n], item, converter, k=k+[n]) for n,
                item in enumerate(data)])


