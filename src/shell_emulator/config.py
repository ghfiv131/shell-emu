"""Параметры командной строки эмулятора."""

import argparse
import os
from dataclasses import dataclass
from typing import Optional

from shell_emulator.shell import DEFAULT_VFS_NAME


@dataclass
class Config:
    """Настройки запуска эмулятора.

    :ivar vfs_path: путь к физическому расположению VFS.
    :ivar script_path: путь к стартовому скрипту.
    """

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None

    @property
    def vfs_name(self):
        """Имя VFS: имя файла без расширения либо имя по умолчанию."""
        if not self.vfs_path:
            return DEFAULT_VFS_NAME
        base = os.path.basename(os.path.normpath(self.vfs_path))
        return os.path.splitext(base)[0] or DEFAULT_VFS_NAME

    def debug_lines(self):
        """Вернуть строки отладочного вывода всех параметров."""
        return [
            f"[debug] vfs_path    = {self.vfs_path!r}",
            f"[debug] vfs_name    = {self.vfs_name!r}",
            f"[debug] script_path = {self.script_path!r}",
        ]


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту",
    )
    return parser


def parse_args(argv=None):
    """Разобрать аргументы ``argv`` и вернуть :class:`Config`."""
    namespace = build_parser().parse_args(argv)
    return Config(namespace.vfs_path, namespace.script_path)
