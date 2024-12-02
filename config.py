from dotenv import load_dotenv
from os import environ

load_dotenv()

class Config:
    TG_TOKEN = environ["TG_TOKEN"]
    SQLITE_DSN = environ["SQLITE_DSN"]

