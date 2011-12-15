import csv
import urllib2
import time
import threading

domain = 'https://graphite-phx.mozilla.org/'
url = '%s' % domain + 'render/?width=586&height=308&target=sumSeries%28stats.addons.response.*%29&target=stats.addons.response.200&target=stats.addons.response.301&target=stats.addons.response.302&target=stats.addons.response.403&target=stats.addons.response.404&target=stats.addons.response.405&target=stats.addons.response.500&from=-15minutes&title=15%20minutes&rawData=true'

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
        if 'stats.addons.response' in row[0]:
            key = row[0].split('.')[-1]
        if len(row):
            step, num = row[3].split('|')
            num = [num]
            num.extend(row[4:])
            try:
                num = [float(n) for n in num]
            except ValueError:
                continue
            result[key] = num
    return result

def format(msg, num):
    return '%s status: %.2f/sec average over the last 15 mins (source: http://bit.ly/canook-graphite)' % (msg, sum(num) / len(num))

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
                num = data.get(k, None)
                if not num:
                    continue
                avg = sum(num) / len(num)
                if avg < v[0] or avg > v[1]:
                    phenny.msg('#amo-bots', format(k, num)) 
            time.sleep(300)

    targs = (phenny,)
    t = threading.Thread(target=monitor, args=targs)
    t.start() 

_limits = {'200':[750, 3500], '500':[0, 10], '403':[0, 10]}
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
