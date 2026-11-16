"""Тесты параметров командной строки."""

import contextlib
import io
import unittest

from tests import helpers  # noqa: F401
from shell_emulator.config import Config, parse_args
from shell_emulator.shell import DEFAULT_VFS_NAME


class ConfigTest(unittest.TestCase):
    """Разбор параметров и имя VFS."""

    def test_defaults(self):
        """Без параметров оба пути не заданы."""
        config = parse_args([])
        self.assertEqual(config, Config(None, None))
        self.assertEqual(config.vfs_name, DEFAULT_VFS_NAME)

    def test_all_params(self):
        """Оба параметра заданы."""
        config = parse_args(["--vfs", "/a/disk.json", "--script", "s.txt"])
        self.assertEqual(config.vfs_path, "/a/disk.json")
        self.assertEqual(config.script_path, "s.txt")
        self.assertEqual(config.vfs_name, "disk")

    def test_debug_lines(self):
        """Отладочный вывод содержит все параметры."""
        text = "\n".join(Config("x/fs.json", "run.txt").debug_lines())
        for value in ("x/fs.json", "run.txt", "fs"):
            self.assertIn(value, text)

    def test_unknown_option(self):
        """Неизвестный параметр - ошибка argparse."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["--bad"])


if __name__ == "__main__":
    unittest.main()
