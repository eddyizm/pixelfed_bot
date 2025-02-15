import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Settings:
    def __init__(self):
        self.token = os.getenv('TOKEN')
        self.app_log = os.getenv('APP_LOG')
        self.account_id = os.getenv('ACCOUNT_ID')
        self.likes_per_session = 10


class PixelFedBotException(Exception):
    pass
