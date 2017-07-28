#http://docs.python-requests.org/en/master/user/advanced/#socks
#sudo pip install requests[socks]
from stem import Signal
from stem.control import Controller
from stem import CircStatus
from urllib2 import HTTPError
from httplib import BadStatusLine
from time import sleep
import json
import urllib2
import socks
from sockshandler import SocksiPyHandler

import logging
logger = logging.getLogger(__name__)


def check_tor(password, port=9051):
    with Controller.from_port(port=port) as controller:
        controller.authenticate(password=password)
        controller.signal(Signal.NEWNYM)
        print controller.is_alive()

        for circ in controller.get_circuits():
            if circ.status != CircStatus.BUILT:
                continue

            exit_fp, exit_nickname = circ.path[-1]

            exit_desc = controller.get_network_status(exit_fp, None)
            exit_address = exit_desc.address if exit_desc else 'unknown'

            logger.info("[+] Exit relay")
            logger.info("    fingerprint: {}".format(exit_fp))
            logger.info("    nickname: {}".format(exit_nickname))
            logger.info("    address: {}".format(exit_address))

def get_home_ip():
    home_opener = urllib2.build_opener()
    foo = home_opener.open("https://check.torproject.org/api/ip")
    home_ip = json.loads(foo.read())['IP']
    home_opener.close()
    return home_ip

home_ip = get_home_ip()


proxy = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, "127.0.0.1", 9050))
#proxy.add_handler(urllib2.HTTPErrorProcessor())
#urllib2.install_opener(proxy)

def check_ip():
    r = proxy.open("https://check.torproject.org/api/ip")
    data = r.read()

    response = json.loads(data)
    if response['IsTor'] != True:
        print "{} is not a safe IP".format(response['IP'])
    print "Public IP: {}".format(response['IP'])
    if len(home_ip.split('.')) != 4 or response['IP'] == home_ip:
        print "oh shit, nard face!"
        exit()
    return response['IP']

check_ip()
