import unittest
import schemaish
from datetime import date, time
from convertish.convert import json_converter,  ConvertError



class TestJSONConverters(unittest.TestCase):

    def test_integer_to_json_conversion(self):
        type = schemaish.Integer()

        value_expected = [
            (0,0),
            (1,1),
            (1L,1),
        ]
        for value, expected in value_expected:
            actual = json_converter(type).from_type(value)
            self.assertEquals(actual,expected)

        value_expected = [
            (0,0),
            (1,1),
            (20,20),
        ]
        for value, expected in value_expected:
            actual = json_converter(type).to_type(value)
            self.assertEquals(actual,expected)

    def test_date_json_conversion(self):
        type = schemaish.Date()
        value = date(1966,12,18)
        actual = json_converter(type).from_type(value)
        expected= {'__type__':'date','year':1966,'month':12,'day':18}
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)
        self.assertRaises(ConvertError, json_converter(type).to_type, 'nonsense')
        self.assertRaises(ConvertError, json_converter(type).to_type, '1990-1-1andabit')

    def test_time_json_conversion(self):
        type = schemaish.Time()
        value = time(11,12,30,500000)
        actual = json_converter(type).from_type(value)
        expected= {'__type__':'time','hour':11,'minute':12,'second':30,'microsecond':500000}
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)
        self.assertRaises(ConvertError, json_converter(type).to_type, 'nonsense')
        self.assertRaises(ConvertError, json_converter(type).to_type, '1990-1-1andabit')

    def test_float_json_conversion(self):
        type = schemaish.Float()
        value = 1.28
        expected = 1.28
        actual = json_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_boolean_json_conversion(self):
        type = schemaish.Boolean()
        value = True
        expected = True
        actual = json_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)

        value = False
        expected = False
        actual = json_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)



    def test_sequencestring_json_conversion(self):
        type = schemaish.Sequence(schemaish.Integer())
        value = [1,2,3,4]
        expected = value
        actual = json_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_sequenceboolean_json_conversion(self):
        type = schemaish.Sequence(schemaish.Boolean())
        value = [True,False,True,True]
        expected = value
        actual = json_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)


    def test_sequencesequenceinteger_json_conversion(self):
        type = schemaish.Sequence(schemaish.Sequence(schemaish.Integer()))
        value = [[1,2,3],[4,5,6]]
        expected = value
        actual = json_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)

    def test_sequencetupleintegerstring_json_conversion(self):
        type = schemaish.Sequence(schemaish.Tuple((schemaish.Integer(),schemaish.String())))
        value = [(1,'1'),(2,'2')]
        expected = value
    
        actual = json_converter(type).from_type(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = json_converter(type).to_type(value)
        self.assertEquals(actual,expected)

if __name__ == '__main__':
    unittest.main()
