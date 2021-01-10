import json
from pathlib import Path

from pyctx.context import Context

import urllib.request
import urllib.parse


file_name = Path(__file__).name.replace('.py', '')  # Extract filename to use as context type


def send_request(ctx: Context):
    with ctx.log.timeit('req1'):
        url = "https://api.ipify.org?format=json"
        f = urllib.request.urlopen(url)
        raw_body = f.read().decode('utf-8')
        with ctx.log.timeit('req1.deserialize'):
            data = json.loads(raw_body)
            return data['ip']


def main():
    ctx = Context(file_name)
    ip_address = send_request(ctx)
    ctx.log.set_data('my/ip.addr', ip_address)
    to_log = ctx.finalize()
    print(json.dumps(to_log))
    """
    {
     "type": "example_api_call", "ctxId": "eed680f1-f375-4516-9c04-0023413a3d94",
     "startTime": "2021-01-10 10:00:39.341488", "endTime": "2021-01-10 10:00:40.208012",
     "data": {"my": {"ip.addr": "31.142.99.204"}},
     "timers": {"ALL": 0.866066, "req1": 0.866007, "req1.deserialize": 7.2e-05},
     "pid": 30545, "thread_name": "MainThread"
    }
    """


if __name__ == '__main__':
    main()
