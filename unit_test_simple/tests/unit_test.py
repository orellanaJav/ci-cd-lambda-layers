import unittest
from unit_test_simple.unit_test_simple import unit_test_simple


class ExampleTestCase(unittest.TestCase):
    """
    Esto es solo un ejemplo de como debes realizar test unitarios a tus
    funciones.
    """

    def test_lambda_handler(self):
        handler = unit_test_simple({})
        self.assertEqual(handler, True)

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()
