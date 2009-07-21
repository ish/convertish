from cStringIO import StringIO
import unittest
import schemaish
import schemaish.type
from datetime import date
from convertish.convert import string_converter, datetuple_converter, ConvertError



class TestConverters(unittest.TestCase):

    def test_integer_to_string_conversion(self):
        type = schemaish.Integer()

        value_expected = [
            (0,'0'),
            (1,'1'),
            (1L,'1'),
        ]
        for value, expected in value_expected:
            actual = string_converter(type).from_type(value)
            self.assertEquals(actual,expected)

        value_expected = [
            ('0',0),
            ('1',1),
            ('20',20),
        ]
        for value, expected in value_expected:
            actual = string_converter(type).to_type(value)
            self.assertEquals(actual,expected)

    def test_date_string_conversion(self):
        type = schemaish.Date()
        value = date(1966,12,18)
        expected = '1966-12-18'
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)
        self.assertRaises(ConvertError, string_converter(type).to_type, 'nonsense')
        self.assertRaises(ConvertError, string_converter(type).to_type, '1990-1-1andabit')

    def test_float_string_conversion(self):
        type = schemaish.Float()
        value = 1.28
        expected = '1.28'
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_boolean_string_conversion(self):
        type = schemaish.Boolean()
        value = True
        expected = 'True'
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)

        value = False
        expected = 'False'
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_file_string_converstion(self):
        # Just for my sanity.
        FileType = schemaish.type.File
        # Reference type.
        type = schemaish.File()
        # Check that it can't be converted without a file-like.
        self.assertRaises(ValueError, string_converter(type).from_type,
                          FileType(None, None, None))
        # Check that the file-likes content are returned.
        self.assertTrue(string_converter(type).from_type(FileType(StringIO('foo'), None, None)) == 'foo')
        # Check that a string is converted to a file.
        file = string_converter(type).to_type('foo')
        self.assertTrue(file.mimetype == 'text/plain')
        self.assertTrue(file.filename == 'content.txt')
        self.assertTrue(file.file.read() == 'foo')

    def test_date_datetuple_conversion(self):
        type = schemaish.Date()
        value = date(1966,12,18)
        expected = (1966,12,18)
        actual = datetuple_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = datetuple_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_sequencestring_string_conversion(self):
        type = schemaish.Sequence(schemaish.Integer())
        value = [1,2,3,4]
        expected = '1,2,3,4'
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_sequenceboolean_string_conversion(self):
        type = schemaish.Sequence(schemaish.Boolean())
        value = [True,False,True,True]
        expected = 'True,False,True,True'
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)


    def test_sequencesequenceinteger_string_conversion(self):
        type = schemaish.Sequence(schemaish.Sequence(schemaish.Integer()))
        value = [[1,2,3],[4,5,6]]
        expected = '1,2,3\n4,5,6'
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_sequencetupleintegerstring_string_conversion(self):
        type = schemaish.Sequence(schemaish.Tuple((schemaish.Integer(),schemaish.String())))
        value = [(1,'1'),(2,'2')]
        expected = '1,1\n2,2'
    
        actual = string_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = string_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_tuple_noneifying(self):
        schema = schemaish.Tuple([schemaish.Integer(), schemaish.String()])
        converter = string_converter(schema)
        self.assertEquals(converter.from_type((None, None)), ',')
        self.assertEquals(converter.from_type((None, '')), ',')
        self.assertEquals(converter.from_type((None, 'foo')), ',foo')
        self.assertEquals(converter.from_type((1, None)), '1,')
        self.assertEquals(converter.to_type(','), (None, None))
        self.assertEquals(converter.to_type(',foo'), (None, 'foo'))
        self.assertEquals(converter.to_type('1,'), (1, None))


if __name__ == '__main__':
    unittest.main()
