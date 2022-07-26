import json
from functools import wraps
from typing import Dict, Union
from typing import Optional
from typing import Tuple

from settings.config import ALLOW_HEADERS

from .config import ALLOW_ORIGIN

_GENERAL_STATUS_SUCCESS = 200
_GENERAL_STATUS_FAILED = 400
_GENERAL_FLAG_SUCCESS = 'SUCCESS'


class ParserResponse:
    """
    Clase que arma la estructura del response de una función, compuesto por un body que es un dict
    que puede o no estar encriptado por un algoritmo, un statusCode y el headers de cors

    Methods
    -------
    response_data: Método que encripta el contenido de body en caso que "encryptor" se haya
        definido como un método válido en el constructor. En caso contrario se retorna el
        data_to_encrypt tal como se recibió junto al status code.

    :Authors:
        - Belkis Carrasco
        - Yuzmhar Guillén

    :Created:
        - 2020.12.18
    """
    encryptor = None
    target = None

    def __init__(self, **kwargs: Dict) -> Dict:
        self.encryptor = kwargs.get('encryptor')
        self.target = kwargs.get('target')

    def response_data(self, status: int, data_to_encrypt: Dict) -> Dict:
        """
        Método que encripta el contenido de data en caso que "encryptor" se haya definido como un
        método válido en el constructor. En caso contrario se retorna el data_to_encrypt tal como
        se recibió.

        Parameters
        ----------
        status : int
            Código del response (200,400,500, etc)
        data_to_encrypt : dict
            Diccionario con data a encriptar. Debe incluir el uuid de la app enviado en el header
        Returns
        -------
        dict
            - status : str
                Estado de la consulta

        :Authors:
            - Belkis Carrasco
            - Yuzmhar Guillén

        :Created:
            - 2020.12.18
        """
        allow_origin = ALLOW_ORIGIN.get(self.target, '*')
        allow_headers = ','.join(ALLOW_HEADERS)

        if isinstance(data_to_encrypt, dict) and not self.encryptor:
            data_to_encrypt = json.dumps(data_to_encrypt)

        body = self.encryptor(data_to_encrypt) if self.encryptor else data_to_encrypt

        return {
            "statusCode": status,
            "body": body,
            "headers": {
                'Access-Control-Allow-Headers': allow_headers,
                'Access-Control-Allow-Origin': allow_origin
            }
        }


class StatusMessage:
    """
    Clase base para translate

    Methods
    -------
    get_status_message: Obtiene el status y el message del metodo invocado

    :Authors:
        - Miguel Sanchez

    :Created:
        - 2022.03.29
    """
    def get_status_message(self, function_name: Union[str, None]) -> tuple:
        """
        Obtiene el status y el message del metodo invocado

        Parameters
        ----------
        function_name : Union[str, None]
            Nombre de la funcion que lo esta invocando

        Returns
        -------
        tuple
            status: dict
                diccionario status
            message: dict
                diccionario message

        :Authors:
            - Miguel Sanchez

        :Created:
            - 2022.05.04
        """
        upper_function_name = ''
        if function_name:
            upper_function_name = f'_{function_name.upper()}'
        status = getattr(self, f'STATUS{upper_function_name}')
        message = getattr(self, f'MESSAGE{upper_function_name}')
        return (status, message)


class LambdaResponse:
    """
    Clase de respuesta estandarizada para lambdas, se puede enviar una respuesta fallida o exitosa

    Methods
    -------
    failure: metodo que entrega una respuesta fallida
    success: metodo que entrega una respuesta exitosa
    generic: metodo que entrega una respuesta generica

    Attributes
    ----------
    dict_status: dict
        diccionario del status a enviar
    dict_message: dict
        diccionario del message a enviar

    :Authors:
        - Miguel Sanchez

    :Created:
        - 2022.03.29
    """
    dict_status: dict = {}
    dict_message: dict = {}

    def __init__(self, status_message: StatusMessage, function_name: Union[str, None] = None):
        _status_message = status_message()
        self.dict_status, self.dict_message = _status_message.get_status_message(function_name)

    def failure(self,
                name_flag_error: str,
                data: dict = None,
                status_lambda: int = _GENERAL_STATUS_FAILED) -> Tuple[int, dict]:
        """
        Entrega una respuesta rapida del estado y el mensaje, cuando falla

        Parameters
        ----------
        name_flag_error : str
            nombre del error, debe ser el mismo para status y message
        status_lambda : int, optional
            status de respuesta, por defecto es 400

        Returns
        -------
        Tuple[int, dict]
            Devuelve una tupla del estado del lambda a responder y un diccionario con la
            información extra
        """
        return status_lambda, self.__standard_dict(name_flag_error, data)

    def success(self,
                name_flag_success: str = _GENERAL_FLAG_SUCCESS,
                data: dict = None,
                status_lambda: int = _GENERAL_STATUS_SUCCESS) -> Tuple[int, dict]:
        """
        Entrega una respuesta rapida del estado y el mensaje, cuando no falla

        Parameters
        ----------
        status_lambda : int, optional
            status de respuesta, por defecto es 200
        name_flag_success : int, optional
            nombre del exito, debe ser el mismo para status y message, por defecto es 'SUCCESS'
        data : dict, optional
            informacíon extra, por defecto es un diccionario vacío

        Returns
        -------
        Tuple[int, dict]
            Devuelve una tupla del estado del lambda a responder y un diccionario con la
            información extra
        """
        return status_lambda, self.__standard_dict(name_flag_success, data)

    def generic(self,
                name_flag: str,
                data: dict,
                status_lambda: int) -> Tuple[int, dict]:
        """
        Entrega una respuesta generica y rapida

        Parameters
        ----------
        status_lambda : int
            status de respuesta
        name_flag_success : int
            nombre del exito, debe ser el mismo para status y message.
        data : dict
            informacíon extra

        Returns
        -------
        Tuple[int, dict]
            Devuelve una tupla del estado del lambda a responder y un diccionario con la
            información extra
        """
        return status_lambda, self.__standard_dict(name_flag, data)

    def generic_mobile(self,
                       name_flag: str,
                       data: dict,
                       status_lambda: int,
                       uuid: str) -> Tuple[int, dict]:
        """
        Entrega una respuesta generica y rapida.

        Parameters
        ----------
        status_lambda : int
            status de respuesta
        name_flag_success : int
            nombre del exito, debe ser el mismo para status y message
        data : dict
            informacíon extra

        Returns
        -------
        Tuple[int, dict]
            Devuelve una tupla del estado del lambda a responder y un diccionario con la
            información extra
        """
        return status_lambda, self.__mobile_dict(name_flag, data, uuid)

    def __standard_dict(self, name_flag_success: str, data: Optional[dict]) -> dict:
        """
        Devuelve un diccionario estandar para comunicarse con otros lambdas
        Por ejemplo:
        {
            'status': 1,
            'message': 'Esto es un mensaje de exito',
            'data': {
                'informacion_extra_1': ''
                'informacion_extra_2': 10
                'informacion_extra_3': True
            }
        }

        Parameters
        ----------
        name_flag_success : str
            nombre del exito, debe ser el mismo para status y message
        data : Optional[dict]
            data opcional, información adicional a la respuesta

        Returns
        -------
        dict
            diccionario con un status, message y data que es opcional
        """
        return dict(
            status=self.dict_status[name_flag_success],
            message=self.dict_message[name_flag_success],
            data=data or {}
        )

    def __mobile_dict(self, name_flag_success: str, data: Optional[dict], uuid: str) -> dict:
        """
        Devuelve un diccionario estandar para mobile
        Por ejemplo:
        {
            'status': 1,
            'message': 'Esto es un mensaje de exito',
            'data': {
                'informacion_extra_1': ''
                'informacion_extra_2': 10
                'informacion_extra_3': True
            },
            'uuid': 'sadsa-asdasd-asdasd-asdsa'
        }

        Parameters
        ----------
        name_flag_success : str
            nombre del exito, debe ser el mismo para status y message
        data : Optional[dict]
            data opcional, información adicional a la respuesta
        uuid : str
            Uuid para mobile

        Returns
        -------
        dict
            diccionario con un status, message y data que es opcional
        """
        return dict(
            status=self.dict_status[name_flag_success],
            message=self.dict_message[name_flag_success],
            data=data or {},
            uuid=uuid
        )


def lambda_response(status_message: StatusMessage):
    """
    Decorador que empaqueta en un diccionario las respuestas estandar para el lambda, la función
    que adquiera este decorador puede devolver hasta 3 datos en la tupla.

    Parameters
    ----------
    status_message: StatusMessage
        Clase para obtener los distintos status o message de la función.

    El metodo debe retornar una tupla con el siguiente orden:

        (flag, data, extras)

    flag: str by default: 'SUCCESS'
        Nombre del status y el message (deben ser el mismo).

    data: dict by default: {}
        Diccionario con información de retorno por si se necesita.

    extras: dict by default: {}
        Diccionario con información extra para el retorno.

        - status: int, Optional by default: 200
            respuesta del lambda en el caso de que tenga que devolverlo a alguna API

        - uuid: str, Optional by default: None
            Identificador unico que permite saber a que usuario se le esta haciendo la llamada
            mediante la app


    Por ejemplo:
        Si la función devuelve una tupla con el flag 'SUCCESS' y la data vacía:

            @lambda_response(Translate):
            def test():
                return ('SUCCESS', {})

        la respuesta sería:

           (200, {'status': '1', 'message': 'exito', 'data': {}})


        Otras maneras de enviar la data
        -------------------------------

        Opción 1:

            @lambda_response(Translate):
            def test():
                return ('ERROR', {'status': False})

        la respuesta sería:

           (200, {'status': '2', 'message': 'Ocurrio un error', 'data': {'status': False}})


        Opción 2:

            @lambda_response(Translate):
            def test():
                return ('ERROR', {'status': False}, {'status': 400})

        la respuesta sería:

           (400, {'status': '2', 'message': 'Ocurrio un error', 'data': {'status': False}})


        Opción 3:

            @lambda_response(Translate):
            def test():
                return (
                    'ERROR',
                    {'status': False},
                    {'status': 400, 'uuid': 'asdasda-asdasdsa-asdsadas'}
                )

        la respuesta sería:

            (
               400,
                {
                   'status': '2',
                   'message': 'Ocurrio un error',
                   'data': {'status': False},
                   'uuid': 'asdasda-asdasdsa-asdsadas'
                }
            )

    :Authors:
        - Miguel Sanchez

    :Created:
        - 2022.04.06
    """
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            _lambda_response = LambdaResponse(status_message, function.__name__)
            name_flag = None
            data = {}
            status_lambda = _GENERAL_STATUS_SUCCESS
            uuid = None

            response = function(*args, **kwargs)
            if len(response) >= 2:
                name_flag = response[0]
                data = response[1]
            else:
                raise Exception(
                    f'Se esperaban 2 items en la tupla de salida. Obtuvimos: {len(response)}'
                )

            if len(response) >= 3:
                extras_dict = response[2]
                _status_lambda = extras_dict.get('status')
                if _status_lambda:
                    status_lambda = _status_lambda
                uuid = extras_dict.get('uuid')

            return (_lambda_response.generic_mobile(name_flag, data, status_lambda, uuid)
                    if uuid else _lambda_response.generic(name_flag, data, status_lambda))
        return wrapper
    return decorator
