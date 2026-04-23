from __future__ import annotations

import unittest

from notes.runtime import cleanup_runtime, main


class FakeController:
    def __init__(self, should_fail: bool = False) -> None:
        self.cleaned = False
        self.should_fail = should_fail

    def cleanup(self) -> bool:
        self.cleaned = True
        if self.should_fail:
            raise RuntimeError("cleanup failed")
        return True


class FakeRuntime:
    def __init__(self, should_fail: bool = False, cleanup_should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.controller = FakeController(cleanup_should_fail)

    def run(self) -> int:
        if self.should_fail:
            raise RuntimeError("runtime failed")
        return 7


class RuntimeTests(unittest.TestCase):
    def test_main_logs_startup_factory_failure(self) -> None:
        crashes: list[str] = []
        stderr: list[str] = []

        def broken_factory():
            raise RuntimeError("startup failed")

        exit_code = main(runtime_factory=broken_factory, crash_logger=crashes.append, stderr_writer=stderr.append)

        self.assertEqual(exit_code, 1)
        self.assertEqual(len(crashes), 1)
        self.assertIn("startup failed", crashes[0])
        self.assertEqual(len(stderr), 1)

    def test_main_logs_runtime_failure_and_cleans_up(self) -> None:
        crashes: list[str] = []
        stderr: list[str] = []
        runtime = FakeRuntime(should_fail=True)

        exit_code = main(runtime_factory=lambda: runtime, crash_logger=crashes.append, stderr_writer=stderr.append)

        self.assertEqual(exit_code, 1)
        self.assertTrue(runtime.controller.cleaned)
        self.assertEqual(len(crashes), 1)
        self.assertIn("runtime failed", crashes[0])

    def test_cleanup_runtime_logs_cleanup_failure(self) -> None:
        crashes: list[str] = []
        stderr: list[str] = []
        runtime = FakeRuntime(cleanup_should_fail=True)

        cleanup_runtime(runtime, crashes.append, stderr.append)

        self.assertTrue(runtime.controller.cleaned)
        self.assertEqual(len(crashes), 1)
        self.assertIn("cleanup failed", crashes[0])
        self.assertEqual(len(stderr), 1)

    def test_main_returns_runtime_exit_code(self) -> None:
        runtime = FakeRuntime()

        exit_code = main(runtime_factory=lambda: runtime, crash_logger=lambda _: None, stderr_writer=lambda _: None)

        self.assertEqual(exit_code, 7)
        self.assertTrue(runtime.controller.cleaned)


if __name__ == "__main__":
    unittest.main()
