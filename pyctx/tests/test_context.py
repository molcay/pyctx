import json
from unittest import TestCase

from ..context import Context, RequestContext, ContextLog


class TestContext(TestCase):
    def test_context_type(self):
        ctx = RequestContext({})
        self.assertTrue(isinstance(ctx, Context))
        self.assertTrue(isinstance(ctx, RequestContext))
        self.assertTrue(isinstance(ctx.log, ContextLog))

    def test_context(self):
        ctx = RequestContext({})
        ctx.set_http_data({})
        ctx.set_response({})
        dict_to_log = ctx.finalize()

        against = {
            'data': {},
            'http': {},
            'type': 'REQ',
            'ctxId': ctx.context_id,
            'startTime': ctx.start_time.strftime(ctx.__TIMESTAMP_FORMAT__),
            'endTime': ctx.end_time.strftime(ctx.__TIMESTAMP_FORMAT__),
            'timers': {
                'ALL': dict_to_log['timers']['ALL'],
                'request': dict_to_log['timers']['request'],
            }
        }

        self.assertDictEqual(dict_to_log, against)

