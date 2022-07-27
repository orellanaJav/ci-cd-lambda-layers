import unittest
from test_layer.test_layer import test_layer


class ExampleTestCase(unittest.TestCase):
    """
    Esto es solo un ejemplo de como debes realizar test unitarios a tus
    funciones.
    """

    def test_lambda_handler(self):
        handler = test_layer({})
        self.assertEqual(handler, True)

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()
