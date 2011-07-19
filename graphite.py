import csv
import urllib2
import time
import threading

domain = 'https://graphite-sjc.mozilla.org/'
url = '%s' % domain + 'render/?width=586&height=308&target=sumSeries%28stats.amo.response.*%29&target=stats.amo.response.200&target=stats.amo.response.301&target=stats.amo.response.302&target=stats.amo.response.403&target=stats.amo.response.404&target=stats.amo.response.405&target=stats.amo.response.500&from=-15minutes&title=15%20minutes&rawData=true'

pwd = open('/home/amckay/.pwd').read().strip()
username = open('/home/amckay/.username').read().strip()

def _pull(msg='500'):
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

    password_mgr.add_password(None, domain, username, pwd)

    handler = urllib2.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)

    # use the opener to fetch a URL
    data = opener.open(url)

    rows = csv.reader(data, delimiter=',')
    result = {}
    for row in rows:
        if 'stats.amo.response' in row[0]:
            key = row[0].split('.')[-1]
        if len(row):
            step, num = row[3].split('|')
            num = [num]
            num.extend(row[4:])
            num = [float(n) for n in num]
            result[key] = num
    return result

def format(msg, num):
    return '%s status: %.2f/sec average over the last 15 mins.' % (msg, sum(num) / len(num))

def pull(msg='500'):
    data = _pull()
    if msg in data:
        return format(msg, data[msg])
    return 'Sorry no idea chuck.'

def setup(phenny):
    def monitor(phenny):
        time.sleep(5) 
	while True:
            data = _pull()
            for k, v in _limits.items():
                num = data[k]
                avg = sum(num) / len(num)
                if avg < v[0] or avg > v[1]:
                    phenny.msg('#amo-bots', format(k, num)) 
            time.sleep(120)

    targs = (phenny,)
    t = threading.Thread(target=monitor, args=targs)
    t.start() 

_limits = {'200':[750, 2000], '500':[0, 2], '403':[0, 1]}
_input = ['200', '301', '302', '403', '404', '405', '500']

def graphite(phenny, inp):
    origterm = inp.groups()[1]
    if not origterm:
        return phenny.say('Syntax: graphite status_code')
    origterm = origterm.encode('utf-8')
    if origterm not in _input:
        return phenny.say('Not in status codes: %s' % ','.join(_input))
    return phenny.say(pull(msg=origterm))

graphite.commands = ['graphite']
graphite.priority = 'high'

if __name__=='__main__':
    print _pull(500)
    #print setup()
