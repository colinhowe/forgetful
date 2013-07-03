import threading
from unittest import TestCase

from mock import patch

import forgetful

@patch('forgetful.error_report', autospec=True)
class TestBackgroundThread(TestCase):
    def tearDown(self):
        forgetful.terminate(wait=True)

    def test_dies(self, mock_client):
        class ChildThread(threading.Thread):
            def run(self):
                self.background_thread = forgetful.BackgroundThread()
                self.background_thread.start()

        child = ChildThread()
        child.start()
        child.join()

        background_thread = child.background_thread
        background_thread.join(2)

        self.assertFalse(background_thread.is_alive())
    
    def test_executes(self, mock_client):
        ev = threading.Event()

        self.called = False
        def dummy_fn(*args, **kwargs):
            self.assertEquals((1, 2), args)
            self.assertEquals({'bob': True}, kwargs)
            self.called = True
            ev.set()
            
        forgetful.queue(dummy_fn, 1, 2, bob=True)

        ev.wait(1)
        self.assertTrue(self.called)
 
    def test_handles_exceptions(self, mock_client):
        ev = threading.Event()
        
        self.called = False
        def raise_exception():
            raise Exception('Blowing it all up')

        def dummy_fn():
            self.called = True
            ev.set()

        forgetful.queue(raise_exception)
        forgetful.queue(dummy_fn)

        ev.wait(1)
        self.assertTrue(self.called)
        self.assertTrue(mock_client.called)
