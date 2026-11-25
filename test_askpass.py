import importlib.machinery
import importlib.util
import io
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "askpass")
loader = importlib.machinery.SourceFileLoader("askpass", PATH)
a = importlib.util.module_from_spec(importlib.util.spec_from_loader("askpass", loader))
loader.exec_module(a)


class Askpass(unittest.TestCase):
    def go(self, argv, allow=True, password=b"s3cret\n"):
        out = types.SimpleNamespace(buffer=io.BytesIO())
        self.log = []
        with mock.patch.object(a, "cmdline", return_value=argv), \
             mock.patch.object(a, "confirm", return_value=allow) as self.confirm, \
             mock.patch.object(a, "ask_password", return_value=password) as self.ask, \
             mock.patch.object(a, "log", lambda *x: self.log.append(x)), \
             mock.patch.object(a.sys, "stdout", out), \
             mock.patch.object(a.sys, "stderr", io.StringIO()):
            return a.main(), out.buffer.getvalue()

    def test_allow(self):
        self.assertEqual(self.go(["sudo", "tee", "/a b"]), (0, b"s3cret\n"))
        self.assertEqual(self.log[0][0], "allowed")
        self.assertEqual(self.log[0][2], "sudo tee '/a b'")
        self.assertNotIn("s3cret", str(self.log))

    def test_block_never_asks_password(self):
        self.assertEqual(self.go(["sudo", "true"], allow=False), (1, b""))
        self.ask.assert_not_called()

    def test_cancel(self):
        self.assertEqual(self.go(["sudo", "true"], password=None), (1, b""))
        self.assertEqual(self.log[0][0], "cancelled")

    def test_not_sudo_and_too_long(self):
        for argv in ([], ["bash"], ["sudo", "x" * 5000]):
            self.assertEqual(self.go(argv), (1, b""))
            self.confirm.assert_not_called()

    def test_hidden_characters_are_shown(self):
        self.go(["sudo", "a\nb‮c"])
        self.assertNotIn("\n", self.log[0][2])
        self.assertNotIn("‮", self.log[0][2])

    def test_kdialog_markup_is_escaped(self):
        with mock.patch.object(a.os, "access", return_value=True), \
             mock.patch.object(a, "run", return_value=b"") as run:
            a.confirm(["x"], "sudo '<b>hi' \\n", "/")
        text = run.call_args[0][0][-1]
        self.assertNotIn("<b>hi", text)
        self.assertNotIn("\\", text)

    def test_log_is_private(self):
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.object(a.pwd, "getpwuid", return_value=types.SimpleNamespace(pw_dir=d)):
            a.log("blocked", ["zsh"], "sudo true")
            p = os.path.join(d, ".local/state/askpass/requests.log")
            self.assertEqual(os.stat(p).st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
