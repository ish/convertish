# -*- coding: utf-8

from cStringIO import StringIO
import unittest
import schemaish
import schemaish.type
from datetime import date, datetime, time

from convertish.convert import ConvertError
from convertish.converters import Converter
from convertish import string_convert, convert, tuple_convert
from convertish.util import SimpleTZInfo


class TestStringConverters(unittest.TestCase):

    def test_integer_to_string_conversion(self):
        type = schemaish.Integer()

        value_expected = [
            (0,'0'),
            (1,'1'),
            (1L,'1'),
        ]
        for value, expected in value_expected:
            actual = Converter().from_type(type, value, None)
            self.assertEquals(actual,expected)

        value_expected = [
            ('0',0),
            ('1',1),
            ('20',20),
        ]
        for value, expected in value_expected:
            actual = Converter().to_type(type, value, None)
            self.assertEquals(actual,expected)

    def test_date_string_conversion(self):
        type = schemaish.Date()
        value = date(1966,12,18)
        expected = '1966-12-18'
        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)
        self.assertRaises(ConvertError, Converter().to_type, type, 'nonsense')
        self.assertRaises(ConvertError, Converter().to_type, type, '1990-1-1andabit')

    def test_float_string_conversion(self):
        type = schemaish.Float()
        value = 1.28
        expected = '1.28'
        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)

    def test_boolean_string_conversion(self):
        type = schemaish.Boolean()
        value = True
        expected = 'True'
        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)

        value = False
        expected = 'False'
        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)

    def test_file_string_converstion(self):
        # Just for my sanity.
        FileType = schemaish.type.File
        # Reference type.
        type = schemaish.File()
        # Check that it can't be converted without a file-like.
        self.assertRaises(ValueError, Converter().from_type, type,
                          FileType(None, None, None))
        # Check that the file-likes content are returned.
        self.assertTrue(Converter().from_type(type, FileType(StringIO('foo'), None, None)) == 'foo')
        # Check that a string is converted to a file.
        file = Converter().to_type(type, 'foo')
        self.assertTrue(file.mimetype == 'text/plain')
        self.assertTrue(file.filename == 'content.txt')
        self.assertTrue(file.file.read() == 'foo')

    def test_sequencestring_string_conversion(self):
        type = schemaish.Sequence(schemaish.Integer())
        value = [1,2,3,4]
        expected = '1,2,3,4'
        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)

    def test_sequenceboolean_string_conversion(self):
        type = schemaish.Sequence(schemaish.Boolean())
        value = [True,False,True,True]
        expected = 'True,False,True,True'
        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)


    def test_sequencesequenceinteger_string_conversion(self):
        type = schemaish.Sequence(schemaish.Sequence(schemaish.Integer()))
        value = [[1,2,3],[4,5,6]]
        expected = '1,2,3\n4,5,6'
        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)

    def test_sequencetupleintegerstring_string_conversion(self):
        type = schemaish.Sequence(schemaish.Tuple((schemaish.Integer(),schemaish.String())))
        value = [(1,'1'),(2,'2')]
        expected = '1,1\n2,2'

        actual = Converter().from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = Converter().to_type(type, value)
        self.assertEquals(actual,expected)

    def test_tuple_unicode(self):
        schema = schemaish.Tuple([schemaish.String(), schemaish.String()])
        converter = Converter()
        self.assertEquals(converter.from_type(schema, ('£1'.decode('utf-8'), u'foo')), '£1,foo'.decode('utf-8'))
        self.assertEquals(converter.to_type(schema, '£1,foo'.decode('utf-8')), ('£1'.decode('utf-8'), u'foo'))

    def test_tuple_noneifying(self):
        schema = schemaish.Tuple([schemaish.Integer(), schemaish.String()])
        converter = Converter()
        self.assertEquals(converter.from_type(schema, (None, None)), ',')
        self.assertEquals(converter.from_type(schema, (None, '')), ',')
        self.assertEquals(converter.from_type(schema, (None, 'foo')), ',foo')
        self.assertEquals(converter.from_type(schema, (1, None)), '1,')
        self.assertEquals(converter.to_type(schema, ','), (None, None))
        self.assertEquals(converter.to_type(schema, ',foo'), (None, 'foo'))
        self.assertEquals(converter.to_type(schema, '1,'), (1, None))

    def test_time_string_conversion(self):
        schema = schemaish.Time()
        converter = Converter()
        tz = SimpleTZInfo(90)
        tests = [(time(1), '01:00:00'),
                 (time(1, 2), '01:02:00'),
                 (time(1, 2, 3), '01:02:03'),
                 (time(1, 2, 3, 4), '01:02:03.000004'),
                 (time(1, 0, 0, 0, tz), '01:00:00+01:30'),
                 (time(1, 2, 0, 0, tz), '01:02:00+01:30'),
                 (time(1, 2, 3, 0, tz), '01:02:03+01:30'),
                 (time(1, 2, 3, 4, tz), '01:02:03.000004+01:30')]
        for t, s in tests:
            self.assertEquals(converter.from_type(schema, t), s)
            self.assertEquals(converter.to_type(schema, s), t)

    def test_datetime_string_conversion(self):
        schema = schemaish.DateTime()
        converter = Converter()
        tz = SimpleTZInfo(90)
        tests = [(datetime(2001, 2, 3, 4, 5, 6), '2001-02-03T04:05:06'),
                 (datetime(2001, 2, 3), '2001-02-03T00:00:00'),
                 (datetime(2001, 2, 3, 4, 5, 6, 7), '2001-02-03T04:05:06.000007'),
                 (datetime(2001, 2, 3, 4, 5, 6, tzinfo=tz), '2001-02-03T04:05:06+01:30'),
                ]
        for t, s in tests:
            self.assertEquals(converter.from_type(schema, t), s)
            self.assertEquals(converter.to_type(schema, s), t)


class TestStringScalarConverters(unittest.TestCase):

    scalar_registry = {
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

    def test_sequencesequenceinteger_string_conversion(self):
        type = schemaish.Sequence(schemaish.Sequence(schemaish.Integer()))
        value = [[1,2,3],[4,5,6]]
        expected = [['1','2','3'],['4','5','6']]
        converter = Converter(registry=self.scalar_registry)
        actual = converter.from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = converter.to_type(type, value)
        self.assertEquals(actual,expected)

class TestSubregistryStringScalarConverters(unittest.TestCase):

    scalar_registry = {
      schemaish.Integer: string_convert.IntegerToStringConverter(),
      schemaish.String: convert.NullConverter(),
      schemaish.Float: string_convert.FloatToStringConverter(),
      schemaish.Date: string_convert.DateToStringConverter(),
      schemaish.Boolean: string_convert.BooleanToStringConverter(),
      schemaish.File: string_convert.FileToStringConverter(),
      schemaish.DateTime: string_convert.DateTimeToStringConverter(),
      schemaish.Sequence: string_convert.SequenceNullConverter(),
      schemaish.Time: string_convert.TimeToStringConverter(),
      schemaish.Tuple: Converter(),
    }

    def test_sequencesequenceinteger_string_conversion(self):
        type = schemaish.Sequence(schemaish.Tuple((schemaish.Integer(),
                                                   schemaish.Integer())))
        value = [(1,2),(4,5)]
        expected = ['1,2','4,5']
        converter = Converter(registry=self.scalar_registry)
        actual = converter.from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = converter.to_type(type, value)
        self.assertEquals(actual,expected)

class TestTupleConverters(unittest.TestCase):

    scalar_registry = {
      schemaish.Date: tuple_convert.DateToDateTupleConverter(),
    }

    def test_date_datetuple_conversion(self):
        type = schemaish.Date()
        value = date(1966,12,18)
        expected = (1966,12,18)
        converter = Converter(registry=self.scalar_registry)
        actual = converter.from_type(type, value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = converter.to_type(type, value)
        self.assertEquals(actual,expected)


if __name__ == '__main__':
    unittest.main()
