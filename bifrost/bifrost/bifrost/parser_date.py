from datetime import date
from datetime import datetime

__version__ = '1.1.0'


def parse_date(arg):
    """
    Transforma una fecha fragmentada en un listado a un tipo de dato date.
​
    Parameters
    ----------
    arg : list
        Listado del tipo:
        - ('31','DIC','2016')
        - ('31','DIC','16')
        - ('31','12','16')
​
    Returns
    -------
    return : datetime
        Fecha formateada del tipo date
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2019-05-30
    """
    months = {
        'ENE': '01',
        'FEB': '02',
        'MAR': '03',
        'ABR': '04',
        'MAY': '05',
        'JUN': '06',
        'JUL': '07',
        'AGO': '08',
        'SEP': '09',
        'OCT': '10',
        'NOV': '11',
        'DIC': '12',
    }
    if len(arg[2]) == 2:
        arg[2] = ''.join(('20', arg[2]))
    return date(int(arg[2]), int(months[arg[1]]), int(arg[0]))


def parse_str_date(arg):
    """
    Transforma una fecha string a tipo date.
​
    Parameters
    ----------
    arg : str
        Fecha en formato:
        - dd/mm/yyyy
        - yyyy/mm/dd
        - dd-mm-yyyy
        - yyyy-mm-dd
        - yyyymmdd
​
    Returns
    -------
    return : datetime
        Fecha formateada del tipo date
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2019-05-30
    """
    try:
        return datetime.strptime(arg, '%d/%b/%Y').date()
    except Exception:
        try:
            return datetime.strptime(arg, '%d/%m/%Y').date()
        except Exception:
            try:
                return datetime.strptime(arg, '%Y%m%d').date()
            except Exception:
                try:
                    return datetime.strptime(arg, '%d-%m-%Y').date()
                except Exception:
                    try:
                        return datetime.strptime(arg, '%Y-%m-%d').date()
                    except Exception:
                        try:
                            return datetime.strptime(arg, '%Y/%m/%d').date()
                        except Exception:
                            pass


def parse_str_datetime(arg):
    """
    Transforma una fecha string a tipo datetime.
​
    Parameters
    ----------
    arg : str
        Fecha en formato:
        - dd/mm/yyyy
        - yyyy/mm/dd
        - dd-mm-yyyy
        - yyyy-mm-dd
        - yyyymmdd
        - yyyy-mm-ddTHH:MM:SSZ
        - yyyy-mm-ddTHH:MM:SS.0Z
        - yyyy-mm-dd HH:MM:SS
​
    Returns
    -------
    return : datetime
        Fecha formateada del tipo datetime
​
    :Authors:
        - Abdel Rojas (Sheep)
​
    :Created:
        - 2019-05-30
    """
    try:
        return datetime.strptime(arg, '%d/%b/%Y')
    except Exception:
        try:
            return datetime.strptime(arg, '%d/%m/%Y')
        except Exception:
            try:
                return datetime.strptime(arg, '%Y%m%d')
            except Exception:
                try:
                    return datetime.strptime(arg, '%d-%m-%Y')
                except Exception:
                    try:
                        return datetime.strptime(arg, '%Y-%m-%d')
                    except Exception:
                        try:
                            return datetime.strptime(arg, '%Y/%m/%d')
                        except Exception:
                            try:
                                return datetime.strptime(arg, '%Y-%m-%dT%H:%M:%SZ')
                            except Exception:
                                try:
                                    return datetime.strptime(arg, '%Y-%m-%d %H:%M:%S')
                                except Exception:
                                    try:
                                        return datetime.strptime(arg, '%Y-%m-%dT%H:%M:%S.%fZ')
                                    except Exception:
                                        try:
                                            return datetime.strptime(arg, '%Y-%m-%dT%H:%M:%S.%f')
                                        except Exception:
                                            try:
                                                return datetime.fromisoformat(arg)
                                            except Exception:
                                                pass
