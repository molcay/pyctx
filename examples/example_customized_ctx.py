import json
import os
from pathlib import Path

from pyctx.context import Context
from pyctx.helpers import JsonObject

file_name = Path(__file__).name.replace('.py', '')  # Extract filename to use as context type


def ctx_id_factory() -> str:
    """A factory method to give ctx id as 8 chars random string"""
    import string
    import random

    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(8))


def extras_factory() -> JsonObject:
    """A factory method to give extras information to log"""
    return {
        'pid': os.getpid(),
        'ppid': os.getppid(),
        'gid': os.getgid(),
        'uid': os.getuid(),
    }


def main():
    ctx = Context(file_name, ctx_id_factory=ctx_id_factory, extras_factory=extras_factory)

    # these will not be in the logged string
    ctx.set('key1', 1)
    ctx.set('key2', 2)
    # these will be in the logged string
    ctx.log.set_data('math/pi', 3.14)
    ctx.log.set_data('math/e', 2.72)

    to_log = ctx.finalize()
    print(json.dumps(to_log))
    """
    {
        "type": "example_customized_ctx", "ctxId": "cyIwzNrc",
        "startTime": "2021-01-10 10:32:20.912046", "endTime": "2021-01-10 10:32:20.912369",
        "data": {"math": {"pi": 3.14, "e": 2.72}},
        "timers": {"ALL": 2.9e-05},
        "pid": 31132, "ppid": 4561, "gid": 20, "uid": 501
    }
    """


if __name__ == '__main__':
    main()
