import json
from os import environ
from traceback import format_exc

import boto3

from settings.config import MULTI_REGION
from settings.config import logger

__version__ = '3.0.0'

AWS_ID_ORGANIZATION = environ.get('AWS_ID_ORGANIZATION', '242956272159')


def connect(service, region):
    """
    Conector de servicios AWS con credenciales temporales.

    Parameters
    ----------
    service : str
        Nombre del servicio a conectar
    region : str
        Identificador de la zona de amazon donde se encuentra el servicio a conectar

    Returns
    -------
    client : Boto3.Client
        Cliente con el acceso autenticado al servicio de AWS

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019-05-30
    """
    AWS_LAMBDA = {
        'AWS_ACCESS_KEY_ID': environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_SESSION_TOKEN': environ.get('AWS_SESSION_TOKEN')
    }
    client = boto3.client(
        service,
        region_name=region,
        aws_access_key_id=AWS_LAMBDA.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=AWS_LAMBDA.get('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=AWS_LAMBDA.get('AWS_SESSION_TOKEN')
    )
    return client


def invoker_dispatch(
    arn=None,
    data=None,
    invocation_type='RequestResponse',
    client=None,
    function_name=None,
    target=None,
    region=None,
    silent=False
):
    """
    Invoca una a otra función lambda, si es una invocación con retorno devuelve un diccionario de
    datos en caso de ser exitoso. Si la invocación es exitosa y asíncrona, el resultado es un bool
    True. Si la respuesta es fallida se retorna un booleano False para ambos tipos de invocación

    Parameters
    ----------
    arn : str
        Ruta identificadora única del recurso AWS a utilizar
    data : dict
        Diccionario de datos que se pasarán como entrada al recurso
    invocation_type: str
        Indica si el tipo de invocación es de forma sincrónica o asincrónica
    client : Boto3.Client
        Cliente de conexión del servicio, si el cliente no existe se crea un nuevo cliente
    function_name : str
        Nombre de la función lambda
    target : str
        Nombre del entorno a ejecutar
    region : str
        Nombre de la región de amazon

    Returns
    -------
    response : dict
        En caso de ser exitosa y ser una llamada síncrona, se retorna el diccionario de respuesta
        del servicio
    True : bool
        Si el proceso es asíncrono, se retorna una respuesta positiva indicando que el recurso
        se pudo invocar de forma correcta (acuse de invocación)
    False : bool
        En ambos tipos de invocación, si la consulta falla, se retorna False

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019-05-30
    """
    try:
        if function_name and target:
            arn = AWSLambdaConfig(
                function_name=function_name,
                target=target
            ).arn
        elif function_name and region:
            arn = AWSLambdaConfig(
                function_name=function_name,
                region=region
            ).arn
        elif function_name:
            arn = AWSLambdaConfig(
                function_name=function_name
            ).arn

        if not client:
            client = connect(service='lambda', region=arn.split(':')[3])

        response = client.invoke(
            FunctionName=arn,
            InvocationType=invocation_type,
            Payload=json.dumps(data)
        )
        if response.get('StatusCode') in [200, 202]:
            if not silent:
                logger.success(
                    'Invocación lambda correcta',
                    extra={'arn': arn, 'data': data}
                )
            if invocation_type == 'RequestResponse':
                return json.loads(response['Payload'].read())
            else:
                return True
        else:
            logger.error(
                'Invocación lambda fallida',
                extra={
                    'arn': arn.split(':')[6],
                    'status_code': str(response.get('StatusCode'))
                }
            )
            return False
    except Exception:
        logger.critical(format_exc(), traceback=format_exc())
        return False


def send_message(
    sqs_name: str = None,
    message_body: str = {},
    message_attributes: str = {},
    target: str = None,
    region: str = None,
    client: str = None,
    silent: str = False
) -> None:
    """
    Envía un mensaje a una cola de amazon para ser registrado y luego ser utilizado o drenado por
    otro servicio.

    Parameters
    ----------
    sqs_name : str
        Nombre de la cola alojada en AWS SQS
    messagge_body : dict
        Diccionario de datos que se pasarán como entrada al recurso
    messagge_attributes : dict
        Diccionario de metadatos que quieren ser agregados al registro de cola
    target : str
        Nombre del entorno a ejecutar
    region : str
        Nombre de la región de amazon
    client : Boto3.Client
        Cliente de conexión del servicio, si el cliente no existe se crea un nuevo cliente
    silent : bool
        Indica si realiza la invocación del servicio de forma silenciosa y no muestra un log, por
        defecto el log se encuentra activado

    Returns
    -------
    response : dict
        En caso de ser exitosa y ser una llamada síncrona, se retorna el diccionario de respuesta
        del servicio
    True : bool
        Si el proceso es asíncrono, se retorna una respuesta positiva indicando que el recurso
        se pudo invocar de forma correcta (acuse de invocación)
    False : bool
        En ambos tipos de invocación, si la consulta falla, se retorna False

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2021.01.08
    """
    try:
        if sqs_name and target:
            url = AWSSQSConfig(
                sqs_name=sqs_name,
                target=target
            ).url
        elif sqs_name and region:
            url = AWSSQSConfig(
                sqs_name=sqs_name,
                region=region
            ).url
        elif sqs_name:
            url = AWSSQSConfig(
                sqs_name=sqs_name
            ).url
        else:
            raise Exception(f'Undefined sqs_name or region or target')

        if not client:
            client = connect(service='sqs', region=url.split('.')[1])
        response = client.send_message(
            QueueUrl=url,
            MessageAttributes=message_attributes,
            MessageBody=json.dumps(message_body)
        )

        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') in [200, 202]:
            if not silent:
                logger.success(
                    'Invocación SQS correcta',
                    extra={'url': url, 'message_body': message_body}
                )
            return response.get('MessageId')
        else:
            logger.error(
                'Invocación SQS fallida',
                extra={
                    'sqs': url.split('/')[-1],
                    'status_code': str(response.get('ResponseMetadata', {}).get('HTTPStatusCode'))  # NOQA
                }
            )
            return False
    except Exception:
        logger.critical(format_exc(), traceback=format_exc())
        return False


class Config:
    """

    Methods
    -------
    get_property : Obtiene un atributo de la clase cargada por el constructor

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019.12.17
    """
    region = 'us-west-2'

    def __init__(self, *args, **kwargs):
        self._config = kwargs

    def get_property(self, property):
        """
        Obtiene un atributo de la clase cargada por el constructor.

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019.12.17
        """
        return self._config.get(property)


class AWSLambdaConfig(Config):
    """

    Properties
    ----------
    arn : str
        Dirección arn de función lambda
    name : str
        Nombre de función lambda

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2019.12.17
    """
    @property
    def arn(self):
        """
        Constructor de ARN

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2020.03.05
        """
        function_name = self.get_property('function_name').lower()
        if self.get_property('target'):
            region = MULTI_REGION.get(self.get_property('target').upper())
        elif self.get_property('region'):
            region = self.get_property('region').lower()
        elif not self.get_property('region') and not self.get_property('target'):
            region = environ.get('AWS_REGION')
        if not region:
            raise Exception(f'Undefined Region AWS Lambda for {function_name}')
        return f'arn:aws:lambda:{region}:{AWS_ID_ORGANIZATION}:function:{function_name}'

    @property
    def name(self):
        """
        Nombre de función lambda.

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019.12.17
        """
        function_name = self.get_property('function_name')
        return function_name


class AWSSQSConfig(Config):
    """

    Properties
    ----------
    url : str
        Dirección url de la cola

    :Authors:
        - Abdel Rojas (Sheep)

    :Created:
        - 2021.01.18
    """

    @property
    def url(self):
        """
        Constructor de ARN

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2020.03.05
        """
        region = None
        sqs_name = self.get_property('sqs_name').lower()
        if self.get_property('target'):
            region = MULTI_REGION.get(self.get_property('target').upper())
        elif self.get_property('region'):
            region = self.get_property('region').lower()
        elif not self.get_property('region') and not self.get_property('target'):
            region = environ.get('AWS_REGION')
        if not region:
            raise Exception(f'Undefined Region AWS Lambda for {sqs_name}')

        return f'https://sqs.{region}.amazonaws.com/{AWS_ID_ORGANIZATION}/{sqs_name}'
