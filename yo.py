import re
import time
from datetime import datetime

def yo(phenny, inp):
    phenny.say('Yo! Commands are: commit?, graphite status_code, arecibo domain.name')

yo.commands = ['yo.*?']
yo.priority = 'high'
