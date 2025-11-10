import os
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()


CASE_TYPE_ORDER = ["Modtagede", "Afgjorte"]

DEBUG = os.getenv('DEBUG', 'False') in ['True', 'true']
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')

BYGGESAGER_POSTGRES_DB_HOST = os.getenv("BYGGESAGER_POSTGRES_DB_HOST")
BYGGESAGER_POSTGRES_DB_USER = os.getenv("BYGGESAGER_POSTGRES_DB_USER")
BYGGESAGER_POSTGRES_DB_PASS = os.getenv("BYGGESAGER_POSTGRES_DB_PASS")
BYGGESAGER_POSTGRES_DB_DATABASE = os.getenv("BYGGESAGER_POSTGRES_DB_DATABASE")
BYGGESAGER_POSTGRES_DB_PORT = os.getenv("BYGGESAGER_POSTGRES_DB_PORT")
