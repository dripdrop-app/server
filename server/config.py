from starlette.config import Config

config = Config('.env')

ENVIRONMENT = config.get('ENV', default='None')
DATABASE_URL = config.get('DATABASE_URL')
REDIS_URL = config.get('REDIS_URL')
PORT = config.get('PORT')
API_KEY = config.get('API_KEY')
