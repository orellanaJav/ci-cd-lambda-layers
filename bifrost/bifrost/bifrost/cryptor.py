from os import environ
from base64 import b64decode

from boto3 import client

__version__ = '1.1.0'


def decrypt_var(value=None):
    """
    Desencripta una variable de entorno específica y devuelve su resultado.

    Parameters
    ----------
    value : str
        Cadena de texto a desencriptar

    Returns
    -------
    DECRYPTED : str
        Valor desencriptado con la llave cargada en la variable de entorno

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019-05-30
    """
    ENCRYPTED = environ.get(value)
    DECRYPTED = client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED)).get('Plaintext', '')
    return DECRYPTED


def decrypt_dict(values=[]):
    """
    Desencripta un conjunto de variables de entorno y devuelve un diccionario
    con el nombre de las variables como claves y los resultados desencriptados
    como valores. Si la variable no puede ser desencriptada, se deja tal cual.

    Parameters
    ----------
    values : list <str>
        Listado de valores a desencriptar

    Returns
    -------
    DECRYPTED_DICT : dict
        Diccionario con el nombre de las variables como claves y los valores desencriptados

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019-05-30
    """
    DECRYPTED_DICT = {}
    for key in values:
        ENCRYPTED = environ.get(key)
        try:
            DECRYPTED_DICT[key] = client('kms').decrypt(
                CiphertextBlob=b64decode(ENCRYPTED)).get('Plaintext', '')
        except Exception:
            DECRYPTED_DICT[key] = ENCRYPTED
    return DECRYPTED_DICT
