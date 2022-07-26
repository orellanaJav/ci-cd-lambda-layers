import re

__version__ = '1.0.0'


def parse_str_clean(arg):
    """
    Obtiene solo caracteres simples.
​
    Parameters
    ----------
    arg : str
        Cadena de carácteres a limpiar
​
    Returns
    -------
    return : str
        Cadena de carácteres simples
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2019-05-30
    """
    return re.sub('[\s+]', '', arg)


def parse_str_clean_white(arg):
    """
    Simplifica el múltiple espaciado en un espaciado para una cadena de
    carácteres.
​
    Parameters
    ----------
    arg : str
        Cadena de carácteres a limpiar
​
    Returns
    -------
    return : str
        Cadena de carácteres con espacio simplificado
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2019-05-30
    """
    return " ".join(re.sub('[\s+]', ' ', arg).split())
