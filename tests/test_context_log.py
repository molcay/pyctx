import time
from unittest import TestCase

from pyctx.context import ContextLog, Context


class TestContext(TestCase):
    def test_context_log(self):
        data_against = {'x': 1, 'y': {'z': True}, 'w': [2.72, 3.14, 1.62], 'b1': True, 'b2': False}

        ctx = Context('TEST')
        log = ContextLog(ctx)
        log.set_data('x', 1)
        log.set_data('y/z', True)
        log.add_data('w', 2.72)
        log.add_data('w', 3.14)
        log.add_data('w', 1.62)

        log.set_status('b1', 123123)
        status1 = log.get_status('b1')
        log.set_status('b2', '')
        status2 = log.get_status('b2')
        self.assertTrue(status1)
        self.assertFalse(status2)

        data, timers = log.finalize()

        self.assertDictEqual(data, data_against)
        self.assertTrue('ALL' in timers)
        self.assertDictEqual(timers, {'ALL': timers['ALL']})
        self.assertTrue(log.get_data('x') == 1)
        self.assertTrue(log.get_data('y/z'))

    def test_context_log_timeit(self):
        ctx = Context('TEST')
        log = ContextLog(ctx)

        with log.timeit('timeit/timer1'):
            print("before sleep")
            time.sleep(1)
            print("after 1 secs")

        _, timers = log.finalize()

        self.assertTrue('ALL' in timers)
        self.assertTrue('timeit' in timers and 'timer1' in timers['timeit'])
        self.assertDictEqual(timers, {'ALL': timers['ALL'], 'timeit': {'timer1': timers['timeit']['timer1']}})
        self.assertGreaterEqual(timers['timeit']['timer1'], 1)

    def test_context_log_timer(self):
        ctx = Context('TEST')
        log = ContextLog(ctx)

        log.start_timer('timer1')
        time.sleep(0.1)
        log.start_timer('timer2')
        time.sleep(0.3)
        log.stop_timer('timer2')
        time.sleep(0.1)
        log.stop_timer('timer1')

        _, timers = log.finalize()
        self.assertTrue('timer1' in timers)
        self.assertTrue('timer2' in timers)
        self.assertGreaterEqual(timers['timer1'], 0.5)
        self.assertGreaterEqual(timers['timer2'], 0.3)
        self.assertLess(timers['timer2'], 0.5)
