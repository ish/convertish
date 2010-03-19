

import unittest
import schemaish
from datetime import date, time
from convertish.converters import YAMLConverter
from convertish.convert import  ConvertError



class TestYAMLConverters(unittest.TestCase):

    def test_structure_yaml_conversion(self):
        type = schemaish.Structure()
        subkey = schemaish.Structure()
        subsubkey = schemaish.Sequence(schemaish.Integer())
        subkey.add('x', schemaish.Integer())
        subkey.add('y', subsubkey)
        type.add('b', subkey)

        value = {'b': {'x': 4, 'y': [1,2,3]}}
        actual = YAMLConverter().from_type(type, value)
        expected = "b:\n  x: '4'\n  y: ['1', '2', '3']\n"

        self.assertEqual(actual, expected)
        value, expected = expected, value

        actual = YAMLConverter().to_type(type, value)
        self.assertEqual(actual, expected)

    def test_sequence_yaml_conversion(self):
        type = schemaish.Sequence(schemaish.Integer())

        value = [1,2,3]
        actual = YAMLConverter().from_type(type, value)
        expected = "['1', '2', '3']\n"

        self.assertEqual(actual, expected)
        value, expected = expected, value

        actual = YAMLConverter().to_type(type, value)
        self.assertEqual(actual, expected)



if __name__ == '__main__':
    unittest.main()
