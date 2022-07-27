import os
import pycodestyle
import unittest


class TestCodeFormat(unittest.TestCase):
    def test_conformance(self):
        """
        Se encarga de comprobar el estilo de codigo de todos los archivos
        con extensión .py del lambda, a excepción de los archivos __init__.py
        mediante en estándar PEP-8 utilizando la librería pycodestyle.
        """

        files_to_inspect = []
        for root, dirs, files in os.walk('./'):
            if '.env' not in root:
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        files_to_inspect.append(os.path.join(root, file))

        """Test that we conform to PEP-8."""
        style = pycodestyle.StyleGuide(quiet=False, ignore=['E402'])
        result = style.check_files(files_to_inspect)
        self.assertEqual(result.total_errors, 0,
                         'Found code style errors (and warnings).')
