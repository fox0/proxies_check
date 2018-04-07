import re
import logging
import queue
import threading

import requests

log = logging.getLogger(__name__)

q = queue.Queue()
ls_alife_proxies = []


def main():
    threads = []
    for i in range(32):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    t = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
    for i in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', t):
        q.put(i)

    q.join()
    log.info('ok')


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        try:
            run(item)
        except (IOError, ValueError):
            pass
        except BaseException:
            log.exception('fatal')
        q.task_done()


def run(proxy):
    headers = requests.get('http://httpbin.org/anything', proxies={'http': proxy}).json()['headers']

    black_list = 'X-Proxy-Id', 'X-Bluecoat-Via', 'Range', 'Max-Forwards'
    white_list = 'Accept', 'Host', 'User-Agent', 'Accept-Encoding', 'Connection'
    for i in black_list:
        if i in headers:
            return
    for i in white_list:
        if i not in headers:
            return
        headers.pop(i)

    log.info(headers)
    ls_alife_proxies.append(proxy)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    main()
