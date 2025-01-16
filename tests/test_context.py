from unittest import TestCase

from pyctx.context import Context, RequestContext, ContextLog
from pyctx.helpers import default_extras_factory


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
        extras = default_extras_factory()

        against = {
            'data': {},
            'http': {},
            'type': 'REQ',
            'pid': extras['pid'],
            'thread_name': extras['thread_name'],
            'ctxId': ctx.context_id,
            'reqId': ctx.request_id,
            'startTime': ctx.start_time.strftime(ctx.__TIMESTAMP_FORMAT__),
            'endTime': ctx.end_time.strftime(ctx.__TIMESTAMP_FORMAT__),
            'timers': {
                'ALL': dict_to_log['timers']['ALL'],
            }
        }

        self.assertDictEqual(dict_to_log, against)

    def test_context_methods(self):
        ctx = RequestContext({})
        s, i, b, f = 'val1', 2, True, 2.72
        ctx.set('key1', s) \
            .set('key2', i) \
            .set('key3', b) \
            .set('key4', f)

        self.assertTrue(ctx.get('key', default='val1') == 'val1')
        self.assertTrue(ctx.get('key_x', default='val2', set_if_missing=True) == 'val2')
        self.assertTrue(ctx.get('key_x') == 'val2')
        self.assertTrue(ctx.get('key1') == s)
        self.assertTrue(ctx.get('key2') == i)
        self.assertTrue(ctx.get('key3') == b)
        self.assertTrue(ctx.get('key4') == f)

        ctx.remove('key_x')
        self.assertIsNone(ctx.get('key_x'))

    def test_finalize(self):
        ctx = RequestContext({})
        ctx.log.set_data('x', ctx.start_time)
        ctx.finalize()
