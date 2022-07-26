from .cryptor import decrypt_dict

ENVIRONMENT_ENCRYPT = [
    'DEVELOPMENT_ALLOW_ORIGIN',
    'PRODUCTION_ALLOW_ORIGIN'
]

ENVIRONMENT_DECRYPT = decrypt_dict(ENVIRONMENT_ENCRYPT)


ALLOW_ORIGIN = {
    'Pandora': ENVIRONMENT_DECRYPT.get('DEVELOPMENT_ALLOW_ORIGIN'),
    'Ares': ENVIRONMENT_DECRYPT.get('DEVELOPMENT_ALLOW_ORIGIN'),
    'Production': ENVIRONMENT_DECRYPT.get('PRODUCTION_ALLOW_ORIGIN')
}
