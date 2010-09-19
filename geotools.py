# Copyright (c) 2010 Franz Pletz <fpletz@fnordicwalking.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import subprocess
import shlex
import re
import json

iface = 'wlan0'
tools = [
    {
        'cmd': '/usr/bin/wicd-cli -y -S -l',
        're': r'\d+\t([\dA-F:]+)\t(\d+)\t([^ ]+)',
    },
    {
        'cmd': '/sbin/iwlist %s scan' % iface,
        're': r'Cell \d+ - Address: ([\dA-F:]+)\s+Channel:(\d+)[^-]*Signal level=-\d+ dBm[^"]+ESSID:"([^"]+)"',
    }
]

request = {
  'version': '1.1.0',
  'host': 'maps.google.com',
  'request_address': True,
  'address_language': 'de_DE',
  'wifi_towers': [],
}

def get_wifis():
    for tool in tools:
        try:
            cmdline = shlex.split(tool['cmd'])
            s = subprocess.check_output(cmdline).replace('\n', ' ')
            wifis = [dict(zip(('mac_address', 'channel', 'ssid'), t))
                        for t in re.compile(tool['re']).findall(s)]
        except Exception as e:
            continue

        for d in wifis:
            d.update({
                'mac_address': d['mac_address'].replace(':', '-').lower(),
                'age': 0,
            })

        return wifis

    return None

def get_location(wifis):
    request['wifi_towers'] = wifis
    req = urllib2.Request('https://www.google.com/loc/json', json.dumps(request))
    response = urllib2.urlopen(req)
    r = json.loads(response.read())
    return r['location']

def print_location(loc):
    print '%(latitude)f, %(longitude)f (+-%(accuracy).1f)' % loc
    print '%(street)s %(street_number)s, %(postal_code)s %(city)s, %(region)s, %(country)s (%(country_code)s)' % loc['address']

