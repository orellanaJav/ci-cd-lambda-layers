from os import environ

ACTIVATE = environ.get('ACTIVATE_SENTRY', False)
DSN = environ.get('DSN_SENTRY', "https://17628e6d91af4f53b0bbe93be59830c9@o506841.ingest.sentry.io/6200359")
ENVIRONMENT_NAME = 'development' if environ.get('AWS_REGION', 'sa-east-1') == 'sa-east-1' else 'production'
