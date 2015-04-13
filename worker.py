import redis

import requests
import xml.etree.ElementTree as ET
import time
import json
import re
from email.utils import parsedate_tz

from bs4 import BeautifulSoup

red = redis.StrictRedis(host='localhost', port=6379)

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
    'http://www.rts.rs/page/stories/sr/rss.html': 1,  # 10
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

red.flushdb()


def get_picture(url):
    req = requests.get(url)
    if req is None:
        return ''

    soup = BeautifulSoup(req.content)

    if url[11:12] == 'b':
        div = soup.find('div', {'class': 'article-text'})
    elif url[7:8] == 'b':
        div = soup.find('div', {'class': 'blog-text'})
    elif url[11:12] == '1':
        div = soup.find('article', {'class': None})
    else:
        div = None

    if div is not None:
        img = div.find('img')
        return img['src'] if img else ''
    else:
        return ''


def parse_description(desc):
    r = 'img\ssrc="(.*)"'
    z = re.search(r, desc)
    return z.group(1) if z.group(1) else ''


def update_hashes(url, cnt):
    print 'Starting: ' + url

    try:
        len_hash = str(len(hashDict.keys()))

        data = requests.get(url).content
        parsed = ET.fromstring(data)

        v = parsed[0].find('item')
        v = v.find('pubDate')

        ts = parsedate_tz(v.text)

        if ts > hashDict[url]:
            count = 0
            print 'Parsing: ' + url

            for item in parsed[0].findall('item'):
                count += 1
                if count == 31:
                    break
                hashes = red.lrange('link:' + url, 0, -1)
                link = item.find('link').text
                if link in hashes:
                    break

                if url[11:12] == 'r':
                    parsed_val = parse_description(item.find('description').text)
                else:
                    parsed_val = get_picture(link)

                if parsed_val != '':
                    red.lpush('link:' + url, link)
                    red.lpush('pic:' + url, parsed_val)

            # clear up queue
            red.ltrim('link:' + url, 0, 29)
            red.ltrim('pic:' + url, 0, 29)

            print 'Finished ' + str(cnt) + ' / ' + len_hash

            # Convert to json! :)
            full_l = red.lrange('link:' + url, 0, -1)
            full_p = red.lrange('pic:' + url, 0, -1)
            list_length = len(full_p)
            new_dict = {}
            if list_length > 0:
                print list_length
                for i in range(0, list_length):
                    new_dict[full_l[i]] = full_p[i]

            current_key = 'json:' + url
            json_dump = json.dumps(new_dict)
            red.set(current_key, json_dump)

            hashDict[url] = ts
    except Exception as inst:
        print inst


while True:
    cnt = 1
    for url in hashDict:
        update_hashes(url, cnt)
        cnt += 1

    print 'Parsovanje je gotovo'
    time.sleep(360)
