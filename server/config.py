from starlette.config import Config

config = Config('.env')

ENVIRONMENT = config.get('ENV', default=None)
DATABASE_URL = config.get('DATABASE_URL')
REDIS_URL = config.get('REDIS_URL')
PORT = config.get('PORT')
API_KEY = config.get('API_KEY')
SECRET_KEY = config.get('SECRET_KEY')
GOOGLE_CLIENT_ID = config.get('GOOGLE_CLIENT_ID', default=None)
GOOGLE_CLIENT_SECRET = config.get('GOOGLE_CLIENT_SECRET', default=None)
SERVER_URL = config.get('SERVER_URL')
