from flask import Flask
import json
import redis
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

hashDict = {
    'http://www.b92.net/info/rss/vesti.xml': 1,  # 0
    'http://www.b92.net/info/rss/sport.xml': 1,
    'http://www.b92.net/info/rss/zivot.xml': 1,
    'http://www.b92.net/info/rss/tehnopolis.xml': 1,
    'http://www.b92.net/info/rss/automobili.xml': 1,
    'http://www.b92.net/info/rss/biz.xml': 1,
    'http://www.b92.net/info/rss/news.xml': 1,
    'http://www.b92.net/info/rss/kultura.xml': 1,
    'http://www.b92.net/info/rss/putovanja.xml': 1,
    'http://www.b92.net/info/rss/zdravlje.xml': 1,
    'http://www.rts.rs/page/stories/sr/rss.html': 1,  #10
    'http://www.rts.rs/page/stories/sr/rss/9/politika.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/11/region.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/10/svet.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/57/srbija danas.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/135/hronika.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/125/Dru%C5%A1tvo': 1,
    'http://www.rts.rs/page/stories/sr/rss/13/ekonomija.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/16/kultura.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/691/vreme.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/711/merila vremena.html': 1,
    'http://www.rts.rs/page/stories/sr/rss/245/servisne vesti.html': 1,
    'http://www.rts.rs/page/sport/sr/rss.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/36/fudbal.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/37/ko%C5%A1arka.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/38/tenis.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/39/odbojka.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/131/rukomet.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/40/vaterpolo.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/87/atletika.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/133/auto-moto.html': 1,
    'http://www.rts.rs/page/sport/sr/rss/129/ostali+sportovi.html': 1,
    'http://rs.n1info.com/rss/2/N1-info': 1,
    'http://rs.n1info.com/rss/3/N1-info': 1,
    'http://rs.n1info.com/rss/4/N1-info': 1,
    'http://rs.n1info.com/rss/5/N1-info': 1,
    'http://rs.n1info.com/rss/6/N1-info': 1,
    'http://rs.n1info.com/rss/7/N1-info': 1,
    'http://rs.n1info.com/rss/8/N1-info': 1,
    'http://rs.n1info.com/rss/10/N1-info': 1,
    'http://rs.n1info.com/rss/11/N1-info': 1,
    'http://rs.n1info.com/rss/12/N1-info': 1,
    'http://rs.n1info.com/rss/13/N1-info': 1,
    'http://rs.n1info.com/rss/14/N1-info': 1,
    'http://rs.n1info.com/rss/15/N1-info': 1,
    'http://rs.n1info.com/rss/16/N1-info': 1
}

app = Flask(__name__)
red = redis.StrictRedis(host='localhost', port=6379, db=4)


@app.route('/get-pics/<path:url>')
@crossdomain(origin='*')
def get_pictures_from_xml(url):
    if url not in hashDict:
        print 'Bad request: ' + url
        return '{}'

    a = red.get('json:' + url)
    return a if a else '{}'


@app.route('/parse-pics/<path:url>')
def get_pictures_from_feed(url):
    return url

if __name__ == '__main__':

    app.run()