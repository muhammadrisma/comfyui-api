import os
from settings import DB_NAME, DB_USER, DB_HOST, DB_PORT
from dotenv import load_dotenv
load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")


DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT
}