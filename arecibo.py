import time
import threading
from datetime import datetime
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

srv = 'https://arecibo-phx.mozilla.org'
url = '%s/feed/arecibo-mozilla-private-account/json/?domain=%%s' % srv
view_url = '%s/view/' % srv
list_url = '%s/list/?period=today&domain=' % srv

domains = ['addons.mozilla.org']

pwd = open('/home/amckay/.pwd').read().strip()
username = open('/home/amckay/.username').read().strip()


def _pull(domain, last=0):
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

    password_mgr.add_password(None, 'arecibo-phx.mozilla.org', username, pwd)

    handler = urllib2.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)

    # use the opener to fetch a URL
    data = opener.open(url % domain)

    try:
        data = json.loads(data.read())
    except ValueError, e:
        print "Error", e
        return 
    data = [ row for row in data if int(row['pk']) > int(last)]
    return data
    
def pull(domain):
    data = _pull(domain, 0)
    if not data:
        return 'Sorry, no idea.'
    return format(data[0])
    
def format(data):
    return '%s, %s at %s %s%s' % (data['fields']['status'],
            data['fields']['type'],
            datetime(*(time.strptime(data['fields']['error_timestamp'], '%Y-%m-%d %H:%M:%S')[0:6])),
            view_url, data['pk'])

def format_count(data, domain):
    return '%s error(s) of type(s) %s on %s (source: %s)' % (len(data), ', '.join(sorted(list(set(str(d['fields']['type']) for d in data)))), domain, 'https://bit.ly/canook-amo')

def setup(phenny):
    last = json.load(open('/home/amckay/.arecibo.last'))
    def monitor(phenny):
        time.sleep(120) 
	while True:
            for domain in domains:
                data = _pull(domain, last.get(domain, {}))
                if data:
                    phenny.msg('#amo-bots', format_count(data, domain))
                    last[domain] = data[0]['pk']
            json.dump(last, open('/home/amckay/.arecibo.last', 'wb'))
            time.sleep(600)

    targs = (phenny,)
    t = threading.Thread(target=monitor, args=targs)
    t.start()
    
def arecibo(phenny, inp):
    origterm = inp.groups()[1]
    if not origterm:
        return phenny.say('Syntax: arecibo domain')
    origterm = origterm.encode('utf-8')
    return phenny.say(pull(origterm))

arecibo.commands = ['arecibo']
arecibo.priority = 'high'

if __name__=='__main__':
    last = json.load(open('/home/amckay/.arecibo.last'))
    for domain in domains:
         data = _pull(domain, last.get(domain, 0))
         if data:
             print format_count(data, domain)
             last[domain] = data[0]['pk']
            #time.sleep(600)
    json.dump(last, open('/home/amckay/.arecibo.last', 'wb'))
