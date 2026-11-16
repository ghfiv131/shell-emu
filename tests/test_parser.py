"""Тесты парсера командной строки."""

import unittest

from tests import helpers  # noqa: F401
from shell_emulator.parser import parse


class ParseTest(unittest.TestCase):
    """Разбор строки на команду и аргументы."""

    def test_command_only(self):
        """Команда без аргументов."""
        self.assertEqual(parse("ls"), ("ls", []))

    def test_command_with_args(self):
        """Команда с аргументами."""
        self.assertEqual(parse("ls -l /home"), ("ls", ["-l", "/home"]))

    def test_multiple_spaces(self):
        """Несколько пробелов и табуляций - один разделитель."""
        self.assertEqual(parse("  cd \t  /tmp   "), ("cd", ["/tmp"]))

    def test_empty(self):
        """Пустая строка и строка из пробелов."""
        self.assertIsNone(parse(""))
        self.assertIsNone(parse("   "))


if __name__ == "__main__":
    unittest.main()
