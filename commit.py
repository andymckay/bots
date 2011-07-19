import re
import time
from datetime import datetime
import urllib
try:
    import json
except ImportError:
    import simplejson as json

url = 'http://whatthecommit.com/'
rx = re.compile('<p>(.*?)</p>', re.DOTALL)

def pull():
    data = urllib.urlopen(url).read()
    data = rx.search(data).group(1).strip() 
    return 'How about: %s' % data

def commit(phenny, inp):
    return phenny.say(pull())

commit.commands = ['commit.*?']
commit.priority = 'high'
