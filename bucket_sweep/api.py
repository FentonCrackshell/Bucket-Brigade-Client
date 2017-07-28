from scanner import Scanner
import json
import dateutil.parser
import urllib2
from urllib2 import HTTPError
#import socks
#from sockshandler import SocksiPyHandler

class BrigadeClient(object):

    STATE = 0

    API_PATHS = {
        'register':'/v1/hello',
        'task':'/v1/task/{client_id}',
        'submit':'/v1/task/{client_id}/{task_id}'
    }

    tasks = None

    def __init__(self, config):
        self.config = config


        self.public_opener = urllib2.build_opener()
        c = self.public_opener.open("https://check.torproject.org/api/ip")
        self.home_ip = json.loads(c.read())['IP']

        #if self.config['notor'] is None:
        #    self.tor_opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, "127.0.0.1", 9050))
        #    self.tor_opener.add_handler(urllib2.HTTPErrorProcessor())

    def connect(self):
        # check client
        pass

    def _get_url(self, api_path, **kwargs):
        if api_path not in self.API_PATHS.keys():
            raise ValueError("Invalid api endpoint")
        try:
            url = "http://{}{}".format(self.config['api_servers'][0], self.API_PATHS[api_path].format(**kwargs))
        except IndexError:
            raise ValueError("no api servers in config")
        return url

    def get(self, api_path, **kwargs):
        url = self._get_url(api_path, **kwargs)
        response = self.public_opener.open(url)
        data = json.loads(response.read())
        if data.get('status') == "ok":
            return data, response.code
        else:
            #TODO: log this as warning
            print data.get('message')
            return data, response.code

    def post(self, api_path, **kwargs):
        url = self._get_url(api_path, **kwargs)

        #req = urllib2.Request(url)
        #r = urllib2.urlopen(req, data = kwargs['data'])
        try:
            response = self.public_opener.open(url, data = kwargs['data'])
            data = json.loads(response.read())
            if data.get('status') == "ok":
                return data, response.code
            else:
                #TODO: log this as warning
                print data.get('message')
                return data, response.code
        except HTTPError as response:
            return None, response.code

    def api_get_task(self):
        json, response_code = self.get("task", client_id=self.config['client_key'])
        self.tasks = json['tasks']

    def scan(self, task_id=None):
        scan_task = None
        for task_id, task in self.tasks.items():
            if scan_task is None or dateutil.parser.parse(task['last_scanned']) < dateutil.parser.parse(scan_task['last_scanned']):
                scan_task = task

        # TODO pick oldest task

        if scan_task:
            scanner = Scanner(self.config)
            scanner.set_target(scan_task)
            for bucket in scanner.scan():
                result, code = self.post(
                    'submit',
                    data=json.dumps(bucket),
                    client_id=self.config['client_key'],
                    task_id=task_id)
                if code == 410:
                    return
                elif result.get('message') == 'bucket does not match task':
                    self.api_get_task()
                    scan_task = self.tasks[task_id]
                    scanner.set_target(scan_task)
        else:
            exit("No tasks, i guess")