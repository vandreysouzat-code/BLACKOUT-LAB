
import time
import unittest

from core.execution import ExecutionController


class TestExecutionController(unittest.TestCase):

    def test_initial_state(self):
        controller = ExecutionController(5, 10)

        self.assertFalse(controller.started)
        self.assertFalse(controller.active)
        self.assertFalse(controller.cancelled)

    def test_start_execution(self):
        controller = ExecutionController(5, 10)

        controller.start()

        self.assertTrue(controller.started)
        self.assertTrue(controller.active)

    def test_rejects_second_start(self):
        controller = ExecutionController(5, 10)
        controller.start()

        with self.assertRaises(RuntimeError):
            controller.start()

    def test_stop_execution(self):
        controller = ExecutionController(5, 10)
        controller.start()
        controller.stop()

        self.assertTrue(controller.cancelled)
        self.assertFalse(controller.active)

    def test_wait_requires_start(self):
        controller = ExecutionController(5, 10)

        with self.assertRaises(RuntimeError):
            controller.wait()

    def test_wait_rejects_invalid_interval(self):
        controller = ExecutionController(5, 10)
        controller.start()

        with self.assertRaises(ValueError):
            controller.wait(0)

        with self.assertRaises(ValueError):
            controller.wait(-1)

    def test_wait_returns_false_after_stop(self):
        controller = ExecutionController(5, 10)
        controller.start()
        controller.stop()

        self.assertFalse(controller.wait())

    def test_execution_expires(self):
        controller = ExecutionController(1, 1)
        controller.start()

        time.sleep(1.1)

        self.assertFalse(controller.active)
        self.assertEqual(controller.remaining_seconds, 0)

    def test_raise_if_stopped(self):
        controller = ExecutionController(5, 10)
        controller.start()
        controller.stop()

        with self.assertRaises(RuntimeError):
            controller.raise_if_stopped()

    def test_rejects_duration_above_limit(self):
        with self.assertRaises(ValueError):
            ExecutionController(11, 10)

    def test_rejects_zero_duration(self):
        with self.assertRaises(ValueError):
            ExecutionController(0, 10)

    def test_rejects_boolean_duration(self):
        with self.assertRaises(ValueError):
            ExecutionController(True, 10)

    def test_rejects_invalid_max_duration(self):
        with self.assertRaises(ValueError):
            ExecutionController(5, 0)


if __name__ == "__main__":
    unittest.main()
