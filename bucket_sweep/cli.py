import os 
import json
import logging
import argparse
from api import BrigadeClient

parser = argparse.ArgumentParser(description='Get dat shit for da scanner', prog='Bucket Brigade')
g_options = parser.add_argument_group('optional arguments')
g_options.add_argument('--verbose', '-v', action='count', default=0, help="verbosity 0-4")
g_options.add_argument('--notor', help='Do not user tor', action='store_const', const=True)

args = parser.parse_args()

if args.verbose > 4:
    args.verbose = 4
if args.verbose < 0:
    args.verbose = 0

_verbosity = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
logging.basicConfig(level=_verbosity[args.verbose])
logger = logging.getLogger(__name__)


default_config = {
    "torcontroller": {
        "password":"CHANGE-PASSWORD",
        "port":9051
    },
    "client_key": "CHANGE-KEY",
    "api_servers": ['hostname:port']
}


settings_path = "{}/.bucket_brigade/".format(os.path.expanduser("~"))
config_path = "{}config.json".format(settings_path)

def get_config():
    with open(config_path) as f:
        try:
            return json.load(f)
        except ValueError:
            exit("Invalid JSON data.  Delete the {} file, and re-run to generate a new confg".format(config_path))

def build_config():
    try:
        if not os.path.exists(settings_path):
            os.makedirs(settings_path)
        with open(config_path, "w+") as f:
            json.dump(default_config, f, indent=2)
    except IOError as e:
        exit("Cannot access settings file {}".format(config_path))
    try:
        return get_config()
    except:
        exit("I give up.  Make your own config file.")

try:
    config = get_config()
except IOError:
    config = build_config()

def start():
    logger.debug("running sweep with settings: {}".format(config))
    mixed_args = vars(args)
    mixed_args.update(config)

    client = BrigadeClient(mixed_args)
    client.connect()

    while True:
        client.api_get_task()
        if client.tasks:
            client.scan()
