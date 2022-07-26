import json
from datetime import datetime
from inspect import currentframe
from inspect import stack
from os import environ

import sentry_sdk
from bifrost.logger_config import ACTIVATE
from bifrost.logger_config import DSN
from bifrost.logger_config import ENVIRONMENT_NAME
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

if ACTIVATE:
    sentry_sdk.init(
        dsn=DSN,
        integrations=[AwsLambdaIntegration()],
        environment=ENVIRONMENT_NAME
    )

try:
    # Sólo usado para formato block en docker
    from tabulate import tabulate
except Exception:
    pass

__version__ = '3.1.1'

# ==============================================================================
# CONFIGURACIONES DE COLORES SOLO CON MODO DEBUG
# ==============================================================================
GRAY = '\033[90m'
RED = '\033[91m'
RED_BOLD = '\033[1m\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
END = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

LEVEL = {
    'SPAM': GRAY,
    'ERROR': RED,
    'CRITICAL': RED_BOLD,
    'SUCCESS': GREEN,
    'DEBUG': GREEN,
    'WARNING': YELLOW,
    'VERBOSE': BLUE,
    'NOTICE': PURPLE,
    'HEADER': CYAN,
    'INFO': WHITE
}


class Logger(object):
    """
    Clase constructura de logs estandarizados.

    Attributes
    ----------
    idx : str
        Valor del identificador único
    name_idx : str
        Nombre del identificador único que servirá de tracking en toda la ejecución
    tag_name_idx : str
        Nombre del identificador único que servirá de tracking en toda la ejecución
    debug : bool
        Indica si el log debe ejecutarse en modo debug. True en caso positivo y False en caso
        contrario

    :Authors:
        - Abdel Rojas (Sheep)
        - Bernardo Freitas

    :Created:
        - 2019-05-30
    """
    idx = None
    name_idx = None
    tag_name_idx = ''
    debug = False

    def __init__(self, name_idx):
        self.debug = False
        self.tag_name_idx = ''

        self.tag_name_idx = name_idx

    def basic_loader(self, *args, **kwargs):
        """
        Función básica para carga de variable identificadora en sistema de
        prints.

        Parameters
        ----------
        kwargs : dict
            Diccionario con los datos basicos para cargar el logger: idx, name_idx, debug

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.idx = kwargs.get(self.tag_name_idx, '')
        self.name_idx = self.tag_name_idx
        self.debug = kwargs.get('debug', False)

    def info(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo INFO

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('INFO', message, traceback, extra)

    def success(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo SUCCESS

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('SUCCESS', message, traceback, extra)

    def verbose(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo VERBOSE

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('VERBOSE', message, traceback, extra)

    def spam(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo SPAM

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('SPAM', message, traceback, extra)

    def notice(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo NOTICE

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('NOTICE', message, traceback, extra)

    def warn(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo WARNING

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('WARNING', message, traceback, extra)

    def error(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo ERROR

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('ERROR', message, traceback, extra)

    def critical(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo CRITICAL

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        self.default('CRITICAL', message, traceback, extra)

    def debugger(self, message, traceback=None, extra={}):
        """
        Crea un log de tipo DEBUG

        Parameters
        ----------
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        if self.debug:
            self.default('DEBUG', message, traceback, extra)

    def block(self, message, *args, **kwargs):
        """
        Impresión detallada de los elementos en modo de depuración. Se indica tanto el tipo como
        la línea de ejecución. Este tipo de log no es impreso en modo productivo

        Parameters
        ----------
        kwargs : dict
            Múltiples variables a verificar

        :Authors:
            - Abdel Rojas (Sheep) (Sheep)

        :Created:
            19-06-2019
        """
        if environ.get('LOCAL_INVOKE'):
            kwargs.update(
                {
                    f'{self.retrieve_name(var)}': var
                    for var in args
                }
            )
            if message:
                kwargs[self.retrieve_name(message)] = message

            params = []
            for key, value in kwargs.items():
                params.append([
                    key,
                    type(value).__name__,
                    json.dumps(value, sort_keys=True, indent=4, default=str)
                ])
            table = tabulate(
                params,
                headers=['VAR', 'TYPE', 'VALUE'],
                tablefmt='grid'
            )
            params = json.dumps(kwargs, sort_keys=True, indent=4, default=str)
            separator = '='*80
            self.default(
                'DEBUG',
                '\n'.join((
                    '\n',
                    separator,
                    f'BLOCK DEBUG - Line: {currentframe().f_back.f_lineno}',
                    separator,
                    '\n',
                    table,
                    '\n',
                    separator,
                    params,
                    separator,
                    '\n'
                ))
            )
        else:
            return

    def default(self, level, message, traceback=None, extra={}):
        """
        Formato general de prints.

        Parameters
        ----------
        level : str
            Indica el tipo de log a imprimir
        message : str
            Texto a imprimir como log
        traceback : str
            Texto correspondiente al traceback
        extra : dict
            Diccionario de variables que se quieren imprimir en el log

        :Authors:
            - Abdel Rojas (Sheep)

        :Created:
            - 2019-05-30
        """
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tracking_log = {
            'name_idx': self.name_idx,
            'idx': self.idx,
            'date': date,
            'level': level,
            'message': message,
            'traceback': traceback,
            'extra': extra
        }
        if environ.get('LOCAL_INVOKE'):
            print(LEVEL[level], message, END)
        elif self.debug:
            print(
                '%s|%s [%s][%s] %s |%s|%s'
                % (
                    LEVEL[level],
                    self.idx,
                    date,
                    level,
                    message,
                    json.dumps(tracking_log, default=str),
                    END
                )
            )
        else:
            print(
                '|%s [%s][%s] %s |%s|'
                % (
                    self.idx,
                    date,
                    level,
                    message,
                    json.dumps(tracking_log, default=str)
                )
            )

    def retrieve_name(self, var):
        """
        Entrega el nombre original de la variable

        Parameters
        ----------
        var : any
            Variable de cualquier tipo que debe ser analizado

        Returns
        -------
        name : str
            Nombre de la variable inspeccionada

        :Authors:
            - Abdel Rojas (Sheep) (Sheep)

        :Created:
            19-06-2019
        """
        for frame_inspect in reversed(stack()):
            names = [
                var_name for var_name, var_val in frame_inspect.frame.f_locals.items()
                if var_val is var
            ]
            if names:
                return names[0]
