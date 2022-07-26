import re

__version__ = '1.1.0'


def camel_to_snake(camel_str):
    """
    Convierte un string camel case a formato snake case.
​
    Parameters
    ----------
    camel_str : str
        Texto string camel case a convertir
​
    Returns
    -------
    str
        Texto en snake case
​
    :Authors:
        - Belkis Carrasco
​
    :Created:
        - 2020.09.28
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


def snake_to_camel(snake_str):
    """
    Convierte un string snake case a formato camel case.
​
    Parameters
    ----------
    snake_str : str
        Texto string snake case a convertir
​
    Returns
    -------
    str
        Texto en camel case
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2020.08.13
    """
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def snake_to_pascal(snake_str):
    """
    Convierte un string snake case a formato pascal case.
​
    Parameters
    ----------
    snake_str : str
        Texto string snake case a convertir
​
    Returns
    -------
    str
        Texto en pascal case
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2020.08.13
    """
    words = snake_str.split('_')
    return ''.join([*map(str.title, words)])


def parser_keys(parser, d):
    """
    Verifica el tipo de dato recibido y llama a la función correspondiente para el formateo de
    las claves según una funcion de parser.
​
    Parameters
    ----------
    parser : function
        Función de parseo de llaves string
    d : dict/list
        Diccionario/Lista a tratar
​
    Returns
    -------
    dict
        Diccionario con claves parseadas
​
    :Authors:
        - Belkis Carrasco
​
    :Created:
        - 2020.11.11
    """

    if isinstance(d, dict):
        return parser_dict(parser, d)
    if isinstance(d, list):
        return parser_list(parser, d)


def parser_list(parser, d):
    """
    Transforma el formato de las claves de una lista de diccionarios, según una función de parser.
​
    Parameters
    ----------
    parser : function
        Función de parseo de llaves string
    d : list
        Lista a tratar
​
    Returns
    -------
    list
        Lista con claves parseadas
​
    :Authors:
        - Belkis Carrasco
​
    :Created:
        - 2020.11.11
    """
    out = []

    for value in d:
        if isinstance(value, dict):
            out.append(parser_keys(parser, value))
        elif isinstance(value, list):
            out_list = []
            for item in value:
                if hasattr(item, '__keylist__'):
                    out_list.append(parser_keys(parser, item))
                else:
                    if isinstance(item, dict):
                        out_list.append(parser_keys(parser, item))
                    else:
                        out_list.append(item)
            out.append(out_list)
        else:
            out.append(value)
    return out


def parser_dict(parser, d):
    """
    Transforma el formato de las claves según una funcion de parser de un diccionarios.
​
    Parameters
    ----------
    parser : function
        Función de parseo de llaves string
    d : dict
        Diccionario a tratar
​
    Returns
    -------
    dict
        Diccionario con claves parseadas
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2020.09.23
    """
    out = {}

    for k, v in d.items():
        if isinstance(v, dict):
            out[parser(k)] = parser_keys(parser, v)
        elif isinstance(v, list):
            out[parser(k)] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[parser(k)].append(parser_keys(parser, item))
                else:
                    if isinstance(item, dict):
                        out[parser(k)].append(parser_keys(parser, item))
                    else:
                        out[parser(k)].append(item)
        else:
            out[parser(k)] = v
    return out


def format_rut(rut: str, dv: str = None) -> str:
    """
    Le da el formato canonico al rut chileno '12.345.678-9'.

    Parameters
    ----------
    rut : str
        Puede ser en formato '12345678-9' ó '123456789'
    dv : str
        Cuando el dígito verificador no pertenece al string del rut

    Returns
    -------
    str
        Rut con formateado a '12.345.678-9'

    :Authors:
        - Katherine Bracho

    :Created:
        - 2021.01.28
    """
    rut = rut.replace('-', '') if '-' in rut else rut
    try:
        if dv is None:
            rut_format = '{:,}'.format(int(rut[:-1])).replace(',', '.')
            full_rut = f'{rut_format}-{rut[-1]}'
        else:
            rut_format = '{:,}'.format(int(rut)).replace(',', '.')
            full_rut = f'{rut_format}-{dv}'
        return full_rut
    except Exception:
        return ''
