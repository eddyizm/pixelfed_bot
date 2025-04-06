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
        self.follows_per_day = 1
        self.following_count_max = 100
        self.tags = ['nature', 'photography', 'blackandwhite', 'outdoors', 'naturephotography', 'california', 'architecture']
        self.base_url = 'https://pixelfed.social/'
        self.api_version = 'api/v1/'
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }


class PixelFedBotException(Exception):
    pass
