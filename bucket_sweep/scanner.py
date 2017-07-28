from brutus import Brute
from socks import ProxyConnectionError
from urllib2 import HTTPError
from httplib import BadStatusLine
import urllib2
from time import sleep
from bs4 import BeautifulSoup

regions = [
    "s3",
    "s3.us-east-2",
    "s3-us-west-1",
    "s3-us-west-2",
    "s3.ca-central-1",
    "s3.ap-south-1",
    "s3.ap-northeast-2",
    "s3-ap-southeast-1",
    "s3-ap-southeast-2",
    "s3-ap-northeast-1",
    "s3.eu-central-1",
    "s3-eu-west-1",
    "s3.eu-west-2",
    "s3-sa-east-1"
]

class Scanner(object):

    _brute = None
    retry_limit = 4

    def __init__(self, config):
        self.config = config
        if self.config['notor'] is None:
            from tor import check_tor
            check_tor(password = config['torcontroller']['password'])

    def brute(self, task=None):
        if task is None:
            task = self.task
        if self._brute is None:
            print self.task['target']
            target = self.task['target'].replace('*', self.task['set'][0])
            self._brute = Brute(target, self.task['set'])

        while True:
            yield self._brute.current
            self._brute.current = self._brute.next

    def http_get(self, url, attempt=1):
        if attempt >= self.retry_limit:
            return None, None
        try:
            if self.config['notor'] is None:
                from tor import proxy
                foo = proxy.open(url)
            else:
                o = urllib2.build_opener()
                foo = o.open(url)

        except (ProxyConnectionError):
            print "dun"
            exit()
        except HTTPError as e:
            #print e.code
            #print e.read()
            code = e.code
            ret_val = e.read()
        except BadStatusLine as e:
            print "bad status line on {}, retrying".format(url)
            sleep(attempt)
            return self.http_get(url, attempt+1)
        except Exception as e:
            print e
            print url
            print "GENERAL ERROR. RETRYING"
            sleep(attempt)
            return self.http_get(url, attempt+1)
        else:
            code = foo.code
            ret_val = foo.read()
            foo.close()
        return ret_val, code


    def scan(self):
        z = 0
        blist = self.task['buckets_remaining'] or self.brute()
        for bucket_name in blist:
            if blist != self.task['buckets_remaining']:
                blist = self.task['buckets_remaining']
            bucket = {}
            if z % 20 == 0:
                if self.config['notor'] is None:
                    from tor import check_ip
                    check_ip()
                print bucket_name
            url = 'http://{}.{}.amazonaws.com'.format(bucket_name, self.task['region'])
            xml, response_code = self.http_get(url)
            bucket['region'] = self.task['region']
            bucket['responsecode'] = response_code
            bucket['name'] = bucket_name
            if response_code is None:
                bucket['scancode'] = "GeneralError"
            else:
                soup = BeautifulSoup(xml, 'lxml')
                try:
                    if soup.find('listbucketresult'):
                        bucket['scancode'] = "ListBucketResult"
                        bucket['files'] = self.parse_files(soup, bucket_name)
                    elif soup.find('error'):
                        bucket['scancode'] = soup.find('error').find('code').next_element
                    else:
                        print "Unknown State:"
                        print url
                        print xml
                        break
                    file_count = 0
                    while soup.find('istruncated') and soup.find('istruncated').next_element == 'true':
                        url = 'http://{}.{}.amazonaws.com/?marker={}'.format(bucket_name, self.task['region'], bucket.get('files')[-1]['key'] )
                        xml, response_code = self.http_get(url)
                        soup = BeautifulSoup(xml, 'lxml')
                        if soup.find('listbucketresult'):
                            bucket['scancode'] = "ListBucketResult"
                            bucket['files'] = self.parse_files(soup, bucket_name)
                        file_count += len(bucket.get('files', []))
                        #todo log as info
                        print "FILE COUNT IS {}".format(file_count)
                        yield bucket
                except AttributeError as e:
                    print e
                    print "error:", url
                    print xml
                    break
            yield bucket
            z+=1

    def parse_files(self, xml, bucket):
        cols = {
            'key':unicode,
            'lastmodified':str,
            'etag':str,
            'size':int,
            'storageclass':str
        }

        ret_val = []
        for f in xml.find_all('contents'):
            fi = {}
            for col, tf in cols.items():
                fi[col] = tf(f.find(col).next_element)
            if fi['size'] > 0:
                fi['filesize'] = fi['size']
                fi['ext'] = fi['key'].split('.')[-1].lower()
                fi['bucket_name'] = bucket
                fi['region'] = self.task['region']
                ret_val.append(fi)
        return ret_val

    def set_target(self, task):
        self.task = task
