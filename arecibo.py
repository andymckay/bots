import time
import threading
from datetime import datetime
import urllib
try:
    import json
except ImportError:
    import simplejson as json

url = 'http://amckay-arecibo.khan.mozilla.org/feed/wsey5twu5tqo456ql5uyqhs5tytkqrytqaugffug/json/?domain=%s'
view_url = 'http://amckay-arecibo.khan.mozilla.org/view/'
list_url = 'http://amckay-arecibo.khan.mozilla.org/list/?period=today&domain='

domains = ['addons.allizom.org',]

def _pull(domain, last):
    data = json.loads(urllib.urlopen(url % domain).read())
    if last:
        data = [ row for row in data if int(row['pk']) > int(last)]
    return data
    
def pull(domain):
    data = _pull(domain, None)
    if data:
        return 'Sorry, no idea.'
    return format(data[0])
    
def format(data):
    return '%s, %s at %s %s%s' % (data['fields']['status'],
            data['fields']['type'],
            datetime(*(time.strptime(data['fields']['error_timestamp'], '%Y-%m-%d %H:%M:%S')[0:6])),
            view_url, data['pk'])

def format_count(data, domain):
    return '%s error(s) on %s at %s%s' % (len(data), domain, list_url, domain)

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
