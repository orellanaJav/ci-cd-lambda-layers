import re
import json
from urllib.parse import parse_qs

try:
    from settings.config import OPERATION_ENDPOINT
except Exception:
    OPERATION_ENDPOINT = {}


TARGET = {
    'V1': 'PRODUCTION',
    'PANDORA': 'PANDORA',
    'ARES': 'ARES',
    'PROFILE': 'PROFILE',
    None: 'PRODUCTION',
    'V2': 'PRODUCTION',
    'PANDORA2': 'PANDORA'
}

BLACK_LIST_HEADERS = [
    'Accept',
    'Accept-Encoding',
    'CloudFront-Forwarded-Proto',
    'CloudFront-Is-Desktop-Viewer',
    'CloudFront-Is-Mobile-Viewer',
    'CloudFront-Is-SmartTV-Viewer',
    'CloudFront-Is-Tablet-Viewer',
    'CloudFront-Viewer-Country',
    'Host',
    'Postman-Token',
    'Referer',
    'User-Agent',
    'Via',
    'X-Amz-Cf-Id',
    'X-Amzn-Trace-Id',
    'X-Forwarded-For',
    'X-Forwarded-Port',
    'X-Forwarded-Proto',
]


def parse_event(function):
    """
    Decorador que estandariza los datos de entrada para el event de una lambda invocada tanto por
    API Gateway o invocación directa a un lambda. Traduce los diccionarios a un event convencional
    de una invocación directa aún cuando el API Gateway tenga configurada la conexión de un lambda
    como proxy.

    Parameters
    ----------
    function : object
        Función a envolver

    Returns
    -------
    object
        Retorno de función a ejecutar por flujo normal

    :Authors:
        - Abdel Rojas (Sheep)
        - Angel Valderrama

    :Created:
        - 2020.12.10
    """
    def parse_params_api(dictionary: dict) -> dict:
        """
        Limpia el diccionario de una API Gateway para obtener lo escencial.

        Parameters
        ----------
        dictionary : dict
            Datos de entrada de una invocación lambda

        Returns
        -------
        dict
            Diccionario con los datos justos simulando un event de invocación directa al lambda

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2020.12.10
        """
        params = dictionary.get('queryStringParameters', {}) or {}
        resource = dictionary.get('resource', {})

        if resource:
            target = TARGET.get(resource.split('/')[1].upper()) or 'PRODUCTION'
            params.update({'target': target})

        body = dictionary.get('body') or {}
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except Exception:
                body = {k: v[0] for k, v in parse_qs(body).items()}
            params.update(body)
        else:
            params.update(json.loads(body.get('body', '{}') or '{}'))

        headers = dictionary.get('headers', {})
        [headers.pop(k) for k in BLACK_LIST_HEADERS if headers.get(k)]
        params.update({'headers': headers})
        params.update({'http_method': dictionary.get('httpMethod')})
        params.update({'path_parameters': dictionary.get('pathParameters', {})})
        params.update({'path_endpoint': dictionary.get('path', {})})
        path_endpoint = re.split(f'{target.lower()}|v1', dictionary.get('path', ''))[1]
        params.update(
            {
                'operation_endpoint': OPERATION_ENDPOINT.get(dictionary.get('httpMethod'), {})
                                                        .get(path_endpoint)
            }
        )
        params.pop('no_decrypt') if 'no_decrypt' in params else None
        return params

    def is_api(items: dict) -> bool:
        """
        Determina si los datos de entrada de la invocación corresponde a una llamada API Gateway.

        Parameters
        ----------
        items : dict
            Datos de entrada de una invocación lambda

        Returns
        -------
        bool
            True si es que se ha hecho una invocación desde una API Gateway. False caso contrario.

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2020.12.10
        """
        if items.get('requestContext') and items.get('httpMethod'):
            return True
        return False

    def wrapper(*args, **kwargs) -> dict:
        kwargs = args[0]
        params = parse_params_api(kwargs) if is_api(kwargs) else kwargs
        return function(params, None)

    return wrapper


def parse_event_sqs_unit(function):
    """
    Decorador que estandariza los datos de entrada para el event de una lambda invocada tanto por
    API Gateway o invocación directa a un lambda. Traduce los diccionarios a un event convencional
    de una invocación directa aún cuando el API Gateway tenga configurada la conexión de un lambda
    como proxy.

    Parameters
    ----------
    function : object
        Función a envolver

    Returns
    -------
    object
        Retorno de función a ejecutar por flujo normal

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2021.01.19
    """

    def clean_record(record: dict) -> dict:
        """
        Extrae los elementos del registro necesarios.

        Parameters
        ----------
        record : dict
            Diccionario con la información de un registro encolado en AWS SQS

        Returns
        -------
        dict
            Diccionario con los datos justos simulando un event de invocación directa al lambda

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        item = json.loads(record.get('body')) or {}
        attributes = record.get('attributes')
        item['sqs'] = {
            'message_id': record.get('messageId'),
            'message_attributes': record.get('messageAttributes'),
            'approximate_receive_count': attributes.get('ApproximateReceiveCount'),
            'sent_timestamp': attributes.get('SentTimestamp'),
            'approximate_first_receive_timestamp': attributes.get('ApproximateFirstReceiveTimestamp')  # NOQA
        }
        return item

    def parse_params_sqs(dictionary: dict) -> dict:
        """
        Limpia el diccionario de un AWS SQS para obtener lo escencial.

        Parameters
        ----------
        dictionary : dict
            Datos de entrada de una invocación lambda

        Returns
        -------
        dict
            Diccionario con los datos justos simulando un event de invocación directa al lambda

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        records = dictionary.get('Records', {}) or []
        return clean_record(records[0]) if len(records) == 1 else {}

    def is_sqs(items: dict) -> bool:
        """
        Determina si los datos de entrada de la invocación corresponde a una llamada desde un AWS
        SQS.

        Parameters
        ----------
        items : dict
            Datos de entrada de una invocación lambda

        Returns
        -------
        bool
            True si es que se ha hecho una invocación desde un AWS SQS. False caso contrario.

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        if items.get('Records'):
            return True
        return False

    def wrapper(*args, **kwargs) -> dict:
        kwargs = args[0]
        params = parse_params_sqs(kwargs) if is_sqs(kwargs) else kwargs
        return function(params, None)

    return wrapper


def parse_event_sqs_block(function):
    """
    Decorador que estandariza los datos de entrada para el event de una lambda invocada tanto por
    AWS SQS o invocación directa a un lambda. Traduce los diccionarios a un event convencional
    de una invocación directa. Carga los registros batch (más de un elemento encolado) enviados por
    bloques por AWS SQS para que sean legibles por el lambda.

    Parameters
    ----------
    function : object
        Función a envolver

    Returns
    -------
    object
        Retorno de función a ejecutar por flujo normal

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2021.01.19
    """

    def clean_record(record: dict) -> dict:
        """
        Extrae los elementos del registro necesarios.

        Parameters
        ----------
        record : dict
            Diccionario con la información de un registro encolado en AWS SQS

        Returns
        -------
        dict
            Diccionario con los datos justos simulando un event de invocación directa al lambda

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        item = json.loads(record.get('body')) or {}
        attributes = record.get('attributes')
        item['sqs'] = {
            'message_id': record.get('messageId'),
            'message_attributes': record.get('messageAttributes'),
            'approximate_receive_count': attributes.get('ApproximateReceiveCount'),
            'sent_timestamp': attributes.get('SentTimestamp'),
            'approximate_first_receive_timestamp': attributes.get('ApproximateFirstReceiveTimestamp')  # NOQA
        }
        return item

    def is_sqs(items: dict) -> bool:
        """
        Determina si los datos de entrada de la invocación corresponde a una llamada desde un AWS
        SQS.

        Parameters
        ----------
        items : dict
            Datos de entrada de una invocación lambda

        Returns
        -------
        bool
            True si es que se ha hecho una invocación desde un AWS SQS. False caso contrario.

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        if items.get('Records'):
            return True
        return False

    def wrapper(*args, **kwargs) -> dict:
        kwargs = args[0]
        if is_sqs(kwargs):
            records = kwargs.get('Records', {}) or []
            records = list(map(clean_record, records))
            params = {'records': records}
        else:
            params = kwargs
        return function(params, None)

    return wrapper


def parse_event_dynamo(function):
    """
    Decorador que estandariza los datos de entrada para el event de una lambda invocada tanto por
    DynamoDB o invocación directa a un lambda. Traduce los diccionarios a un event convencional
    de una invocación directa aún cuando el DynamoDB tenga configurado los eventos de streaming en
    cualquiera de sus 4 opciones.

    Parameters
    ----------
    function : object
        Función a envolver

    Returns
    -------
    object
        Retorno de función a ejecutar por flujo normal

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2021.01.19
    """
    DATA_TYPE = {
        'S': str,
        'N': int
    }

    def mutate_values(element) -> dict:
        """
        Transforma el diccionario de datos recibido por dynamo a un diccionario simplificado de
        Clave-Valor plano.

        Parameters
        ----------
        element : list
            Primer elemento contiene el nombre de la columna
            Segundo elemento contiene el tipo de dato y el valor del registro en un diccionario

        Returns
        -------
        tuple
            Clave-Valor con el valor casteado al tipo de dato específico

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.07.02
        """
        key = element[0]
        data_type, value = tuple(element[1].items())[0]
        value = DATA_TYPE.get(data_type)(value)
        return key, value

    def clean_record(record: dict) -> dict:
        """
        Extrae los elementos del registro necesarios.

        Parameters
        ----------
        record : dict
            Diccionario con la información de un registro encolado en AWS Dynamodb

        Returns
        -------
        dict
            Diccionario con los datos justos simulando un event de invocación directa al lambda

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        dynamodb_object = record.get('dynamodb', {})
        item = {
            'trigger_event': record.get('eventName'),
            'stream_type': dynamodb_object.get('StreamViewType'),
            'table_name': record.get('eventSourceARN').split('/')[1]
        }
        keys = dynamodb_object.get('Keys')
        if keys:
            item.update(**{'keys': dict(map(mutate_values, keys.items()))})

        new_image = dynamodb_object.get('NewImage')
        if new_image:
            item.update(**{'new_object': dict(map(mutate_values, new_image.items()))})

        old_image = dynamodb_object.get('OldImage')
        if old_image:
            item.update(**{'old_object': dict(map(mutate_values, old_image.items()))})
        return item

    def parse_params_dynamo(dictionary: dict) -> dict:
        """
        Limpia el diccionario de un AWS SQS para obtener lo escencial.

        Parameters
        ----------
        dictionary : dict
            Datos de entrada de una invocación lambda

        Returns
        -------
        dict
            Diccionario con los datos justos simulando un event de invocación directa al lambda

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        records = dictionary.get('Records', {}) or []
        if len(records) == 1:
            return clean_record(records[0])
        else:
            return {}

    def is_dynamo(items: dict) -> bool:
        """
        Determina si los datos de entrada de la invocación corresponde a una llamada desde un AWS
        DynamoDB.

        Parameters
        ----------
        items : dict
            Datos de entrada de una invocación lambda

        Returns
        -------
        bool
            True si es que se ha hecho una invocación desde un AWS DynamoDB. False caso contrario.

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2021.01.19
        """
        if items.get('Records'):
            return True
        return False

    def wrapper(*args, **kwargs) -> dict:
        kwargs = args[0]
        params = parse_params_dynamo(kwargs) if is_dynamo(kwargs) else kwargs
        return function(params, None)

    return wrapper
