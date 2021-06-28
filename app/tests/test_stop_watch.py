from time import sleep
import unittest

from stop_watch import StopWatch


class StopWatchTest(unittest.TestCase):

    def test_stop_watch(self):
        stop_watch = StopWatch()
        self.assertFalse(stop_watch.is_running())
        self.assertFalse(stop_watch.any_time_elapsed())

        stop_watch.start()
        sleep(0.05)
        self.assertTrue(stop_watch.is_running())
        stop_watch.stop()
        self.assertFalse(stop_watch.is_running())
        self.assertTrue(stop_watch.elapsed_time())
        with self.assertRaises(ValueError):
            self.assertTrue(stop_watch.elapsed_time('BooBoo'))

        stop_watch.start('BooBoo')
        sleep(1.0)
        stop_watch.stop()
        self.assertGreaterEqual(stop_watch.elapsed_time(), 0.05)
        self.assertGreaterEqual(stop_watch.elapsed_time('BooBoo'), 1.0)
        with self.assertRaises(ValueError):
            self.assertTrue(stop_watch.elapsed_time('DooDoo'))

        stop_watch.start('BooBoo')
        sleep(1.0)
        with self.assertRaises(ValueError):
            self.assertTrue(stop_watch.start())
        stop_watch.stop()
        with self.assertRaises(ValueError):
            self.assertTrue(stop_watch.stop())

        self.assertTrue(stop_watch.any_time_elapsed())
        total_elapsed = stop_watch.total_elapsed_time()
        self.assertGreaterEqual(total_elapsed['BooBoo'], 1.0)
        self.assertGreaterEqual(total_elapsed['TOTAL_ELAPSED'], 1.0)

        pretty_elapsed = stop_watch.pretty_elapsed_time()
        self.assertTrue('TOTAL_ELAPSED: ' in pretty_elapsed)
        self.assertTrue('BooBoo: ' in pretty_elapsed)
        self.assertFalse('DooDoo: ' in pretty_elapsed)
