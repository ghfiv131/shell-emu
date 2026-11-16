"""Вспомогательные функции для тестов."""

import io
import os
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from shell_emulator.shell import Shell  # noqa: E402


def make_shell(**kwargs):
    """Создать оболочку с выводом в строковые буферы."""
    out, err = io.StringIO(), io.StringIO()
    return Shell(out=out, err=err, **kwargs), out, err


def feeder(lines):
    """Вернуть функцию-читатель, выдающую строки ``lines`` по очереди."""
    iterator = iter(lines)

    def reader(prompt):
        """Вернуть очередную строку или возбудить EOFError."""
        try:
            return next(iterator)
        except StopIteration:
            raise EOFError from None

    return reader
