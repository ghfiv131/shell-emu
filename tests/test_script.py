"""Тесты выполнения стартового скрипта."""

import contextlib
import io
import os
import tempfile
import unittest

from tests.helpers import make_shell
from shell_emulator.__main__ import main
from shell_emulator.script import run_lines


class RunLinesTest(unittest.TestCase):
    """Выполнение строк скрипта."""

    def test_echo_input_and_output(self):
        """Выводятся и команда с приглашением, и её результат."""
        shell, out, _ = make_shell()
        result = run_lines(shell, ["# comment", "", "ls /x"])
        self.assertTrue(result.ok)
        self.assertEqual(out.getvalue(), "vfs:/$ ls /x\nls: args=['/x']\n")

    def test_stops_on_first_error(self):
        """Выполнение прекращается на первой ошибке."""
        shell, out, err = make_shell()
        result = run_lines(shell, ["ls", "bad", "cd"], name="s.txt")
        self.assertFalse(result.ok)
        self.assertNotIn("cd:", out.getvalue())
        self.assertIn("s.txt:2: error in command 'bad'", err.getvalue())

    def test_exit_in_script(self):
        """exit в скрипте завершает его с кодом."""
        shell, out, _ = make_shell()
        result = run_lines(shell, ["exit 4", "ls"])
        self.assertEqual((result.ok, result.exit_code), (True, 4))
        self.assertNotIn("ls:", out.getvalue())


class MainTest(unittest.TestCase):
    """Запуск эмулятора со стартовым скриптом."""

    def run_main(self, text):
        """Запустить main со скриптом ``text``, вернуть код и вывод."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "start.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write(text)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(err):
                code = main(["--script", path])
        return code, out.getvalue(), err.getvalue()

    def test_script_exit(self):
        """Код возврата берётся из exit."""
        code, out, _ = self.run_main("ls\nexit 7\n")
        self.assertEqual(code, 7)
        self.assertIn("[debug] script_path", out)

    def test_script_error(self):
        """Ошибка в скрипте - код возврата 1."""
        code, _, err = self.run_main("nope\n")
        self.assertEqual(code, 1)
        self.assertIn("script aborted", err)

    def test_missing_script(self):
        """Отсутствующий скрипт - код возврата 2."""
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(err):
            code = main(["--script", "/nonexistent/start.txt"])
        self.assertEqual(code, 2)
        self.assertIn("cannot open startup script", err.getvalue())


if __name__ == "__main__":
    unittest.main()
