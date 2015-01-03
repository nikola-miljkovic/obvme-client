from flask import Flask
import requests
import xml.etree.ElementTree as ET
import json
import re
from email.utils import parsedate_tz

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

app = Flask(__name__)

hashDict = {
    'http://www.b92.net/info/rss/vesti.xml': 1,
    'http://www.b92.net/info/rss/sport.xml': 1,
    'http://www.b92.net/info/rss/zivot.xml': 1,
    'http://www.b92.net/info/rss/tehnopolis.xml': 1,
    'http://blog.b92.net/rss/feed/index.xml': 1,
    'http://www.b92.net/info/rss/news.xml': 1,
    'http://www.b92.net/info/rss/biz.xml': 1,
    'http://www.b92.net/info/rss/kultura.xml': 1,
    'http://www.b92.net/info/rss/automobili.xml': 1,
    'http://www.b92.net/info/rss/putovanja.xml': 1,
    'http://www.b92.net/info/rss/zdravlje.xml': 1,
    'http://www.b92.net/info/rss/video.xml': 1
}

pictureHashes = {}


def get_picture(url):
    rule = 'img src=\"(.*)\" width='
    print 'parsing ' + url
    data = requests.get(url).content
    print 'requesting' + url
    match = re.search(rule, data)
    return match.group(1)


@app.route('/get-pics/<path:url>')
@crossdomain(origin='*')
def get_pictures_from_xml(url):
    if url not in hashDict:
        print 'Bad request: ' + url
        return 'bad request'

    data = requests.get(url).content
    parsed = ET.fromstring(data)

    ts = parsedate_tz(parsed[0].find('pubDate').text)

    if ts > hashDict[url]:
        print 'parsing ' + url
        for item in parsed[0].findall('item'):
            link = item.find('link').text
            pictureHashes[link] = get_picture(link)

        hashDict[url] = ts

    return json.dumps(pictureHashes)


@app.route('/parse-pics/<path:url>')
def get_pictures_from_feed(url):

    return url
