import json
from traceback import format_exc
from typing import Union

import requests

from settings.config import logger

from requests.exceptions import ConnectionError
from requests.exceptions import Timeout

__version__ = '3.11.0'

STATUS_CODES_SUCCESS = [
    requests.codes.ok,
    requests.codes.created,
    requests.codes.accepted,
    requests.codes.non_authoritative_info,
    requests.codes.non_authoritative_information,
    requests.codes.no_content,
    requests.codes.reset_content,
    requests.codes.reset,
    requests.codes.partial_content,
    requests.codes.partial,
    requests.codes.multi_status,
    requests.codes.multiple_status,
    requests.codes.multi_stati,
    requests.codes.multiple_stati,
    requests.codes.already_reported,
    requests.codes.im_used
]


def check_ip() -> str:
    """
    Verifica la ip de la función.

    Returns
    -------
    str
        Dirección IP desde donde se realiza la petición.

    Exceptions
    ----------
    str
        Mensaje de error

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019-05-30
    """
    try:
        source = 'https://api.ipify.org?format=json'
        response = dispatcher_data('GET', source)
        ip = json.loads(response.get('data', {})).get('ip')
        logger.debugger(
            'IP Function', extra={
                'ip': json.loads(response.get('response', {})).get('ip')
            }
        )
        return ip
    except Exception:
        logger.error(
            'No se pudo corroborar la ip, problemas de conexión',
            traceback=format_exc()
        )


def dispatcher_data(method: str, url: str, data: Union[str, dict] = None, extra: dict = {}) -> dict:
    """
    Envía la información recolectada al webservice.

    Parameters
    ----------
    method : str
        Indica el método HTTP a ejecutar
    url : str
        Dirección absoluta del endpoint a ejecutar
    data : dict
        Diccionario de datos que va en el cuerpo de la petición
    extra : dict
        Diccionario con información extra en el proceso de invocación. Puede contener el método
        de autenticación que debe ir en el header de la consulta.
        {
            'auth_type': 'Token',
            'token': <str token>
        }
        También el timeout como int en segundos
        {
            'timeout': <int>
        }
        Incluso headers en general
        {
            'ApplicationId': <str>
        }
        Para hacer envío de un certificado enviar el path en el siguiente diccionario
        {
            'cert': <str>
        }
    Returns
    -------
    response : dict
        Contiene un diccionario con la respuesta del endpoint.
        Si la consulta es positiva:
        {
            'status': True,
            'response': <response>
        }

        Si la consulta es negativa
        {
            'status': False
        }

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019-05-30
    """
    try:
        method = method.upper()
        headers = extra.get('headers', {'Content-Type': 'application/json'})
        if extra.get('token'):
            headers['Authorization'] = ' '.join((
                extra.get('auth_type'),
                extra.get('token')
            ))
        if method == 'GET':
            response = requests.request(
                method=method,
                url=url,
                params=data,
                headers=headers,
                timeout=extra.get('timeout', 4),
                verify=extra.get('cert', True)
            )
        else:
            response = requests.request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                timeout=extra.get('timeout', 4),
                verify=extra.get('cert', True)
            )
        if response.status_code in STATUS_CODES_SUCCESS:
            logger.success('Petición correcta')
            try:
                final_data = {
                    'status': True,
                    'response': response.json(),
                    'status_code': response.status_code
                }
            except Exception:
                final_data = {
                    'status': True,
                    'response': response.text,
                    'status_code': response.status_code
                }
            return final_data
        else:
            logger.error(
                'Petición Fallida',
                extra={
                    'status_code': str(response.status_code),
                    'response': response.text
                }
            )
            try:
                return {
                    'status': False,
                    'response': response.json(),
                    'status_code': response.status_code
                }
            except Exception:
                try:
                    return {
                        'status': False,
                        'response': response.text,
                        'status_code': response.status_code
                    }
                except Exception:
                    return {
                        'status': False,
                        'status_code': response.status_code
                    }
    except Timeout:
        return {'status': False, 'timeout': True}
    except ConnectionError:
        logger.error('Error de conexión', traceback=format_exc())
        return {'status': False}
    except Exception:
        logger.critical(format_exc(), traceback=format_exc())
        return {'status': False}
