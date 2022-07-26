import requests
from os import environ


def validate_captcha(function):
    """
    Decorador que verifica si el token del captcha es cálido.

    Parameters
    ----------
    function : object
        Función a envolver

    Returns
    -------
    object
        Retorno de función a ejecutar por flujo normal

    :Authors:
        - Angel Valderrama
        - Belkis Carrasco

    :Created:
        - 2021.08.16
    """
    def verify(captcha: str) -> bool:
        """
        Verifica la validez del captcha.

        Paramters
        ---------
        captcha : str
            Token a validar

        Returns
        -------
        bool
            True si el token es correcto, False en caso contrario

        :Authors:
            - Angel Valderrama
            - Belkis Carrasco

        :Created:
            - 2021.08.16
        """
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': environ.get('CAPTCHA_SECRET'),
                'response': captcha,
            }
        )

        data = response.json()

        if not data.get('success'):
            return False, data
        return True, data

    def wrapper(*args: list, **kwargs: dict) -> dict:
        """
        Envoltorio para decoración

        Parameters
        ----------
        kwargs : dict
            Datos necesarios para VALIDAR EL CAPTCHA:
            captcha : str
                Token a validar

        :Authors:
            - Angel Valderrama
            - Belkis Carrasco

        :Created:
            - 2021.08.16
        """
        captcha = kwargs.get('data', {}).get('captcha')

        verified, response_verify = verify(captcha)
        kwargs.update(
            {
                'verified_captcha': verified,
                'response_verify': response_verify
            }
        )
        return function(**kwargs)

    return wrapper
