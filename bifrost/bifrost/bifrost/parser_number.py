import re
from typing import Union


__version__ = '1.1.0'


# FLOTANTES EXTRANJERO
def parse_num_str(arg):
    return re.sub('[^0-9.-]', '', str(arg))


def parse_num_float(arg):
    return float(re.sub('[^0-9.]', '', str(arg)))


def parse_num_int(arg):
    return int(re.sub('[^0-9.-]', '', str(arg)).split('.')[0])


def parse_str(arg):
    return re.sub(r'[^a-zA-Z0-9\s]+', '', arg).upper().strip()


# FLOTANTES NACIONALES
def parse_num_float_national(arg):
    return float(re.sub('[^0-9,]', '', str(arg)).replace(',', '.'))


def parse_num_float_national2(arg):
    return float(re.sub('[^0-9]', '', str(arg)))


def parse_amount(amount: Union[int, str]) -> str:
    """
    Asigna formato númerico con separadores decimales.

    Parameters
    ----------
    amount : str|int
        Valor del número entero a asignar formato

    Returns
    -------
    str
        Monto formateado 22.158.333

    :Authors:
        - Katherine Bracho

    :Created:
        - 2021.01.28
    """
    return '{:,}'.format(int(amount)).replace(',', '.')


def parse_str_int(value: str) -> int:
    """
    Devuelve un int con los números encontrados en un string. Puede ser
    negativo también. Idealmente, usar para valores como '$12.000', etc.

    Parameters
    ----------
    value : str
        String que debe ser 'limpiado'.

    Returns
    -------
    int
        El número parseado a int, si es posible. De lo contrario, retorna 0.

    :Authors:
        Gabriel Ruiz

    :Created:
        - 2021.05.07
    """
    numbers = [s for s in value if s.isdigit() or s == '-']
    if '-' in numbers and numbers[0] != '-':
        numbers.remove('-')
    try:
        return int(''.join(numbers))
    except:
        return 0
