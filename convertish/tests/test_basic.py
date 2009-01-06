import unittest
import schemaish
from datetime import date
from convertish.convert import string_converter, datetuple_converter



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

if __name__ == '__main__':
    unittest.main()
