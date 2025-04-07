import logging
import json
import time
from random import randrange

log = logging.getLogger(__name__)


def random_time():
    '''Use this to randomize actions'''
    sleep_time = randrange(5, 120)
    log.info(f'sleeping for {sleep_time} seconds...')
    time.sleep(sleep_time)
    return sleep_time


def write_to_json(data, name: str = 'response'):
    with open(f'{name}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)


def read_json(data):
    with open(data, 'r') as json_file:
        return json.load(json_file)
