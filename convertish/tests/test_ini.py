
import unittest
import schemaish
from datetime import date, time
from convertish.converters import INIConverter
from convertish.convert import  ConvertError



class TestJSONConverters(unittest.TestCase):

    def test_integer_to_json_conversion(self):
        type = schemaish.Structure()
        subkey = schemaish.Structure()
        subsubkey = schemaish.Sequence(schemaish.Integer())
        subkey.add('x', schemaish.Integer())
        subkey.add('y', subsubkey)
        type.add('b', subkey)

        value = {'b': {'x': 4, 'y': [1,2,3]}}
        print INIConverter().registry
        actual = INIConverter().from_type(type, value)
        expected = """[b]
y = [1, 2, 3]
x = 4

"""
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
