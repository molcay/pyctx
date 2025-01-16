CTX
----

[![pipeline status](https://gitlab.com/molcay/pyctx/badges/master/pipeline.svg)](https://gitlab.com/molcay/pyctx/commits/master)
[![coverage report](https://gitlab.com/molcay/pyctx/badges/master/coverage.svg)](https://gitlab.com/molcay/pyctx/commits/master)

Context package to use data between function calls, use timers and log it.

For example; you want to have some decision points in your code, or you want to measure the time spent on a specific calculation or I/O operation:

```python
from pyctx.context import Context

ctx = Context('APP')
x = 100
y = (x + 1) * (x - 1)
ctx.log.set_data('isEven', y % 2)
ctx.log.set_data('y', y)
ctx.log.start_timer('timer1')
import time

time.sleep(1)
ctx.log.stop_timer('timer1')
with ctx.log.timeit('timer2_context_manager'):
    time.sleep(5)

ctx.finalize()
```

- As a return value of the `ctx.finalize()`, you will get python dictionary.
You can use any json serialization to convert the dictionary to string.
Here is the above result:

```json
{
  "type": "APP",
  "ctxId": "0fdecfe0-067e-4bdd-9920-3b7ed46d8a98",
  "startTime": "2019-08-06 09:42:31.222184",
  "endTime": "2019-08-06 09:42:37.236861",
  "data": {
    "isEven": 1,
    "y": 9999
  },
  "timers": {
    "timer1": 1.00633,
    "timer2_context_manager": 5.002412
  }
}
```
