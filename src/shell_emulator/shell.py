"""Ядро эмулятора: выполнение команд и цикл REPL."""

import sys

from shell_emulator.commands import COMMANDS, CommandError, ExitRequest
from shell_emulator.parser import parse
from shell_emulator.vfs import Vfs

DEFAULT_VFS_NAME = "vfs"
SHELL_NAME = "emulator"


class Shell:
    """Состояние сеанса эмулятора и выполнение команд."""

    def __init__(self, vfs=None, out=None, err=None):
        """Создать сеанс.

        :param vfs: загруженная VFS (по умолчанию пустая VFS в памяти).
        :param out: поток для обычного вывода (по умолчанию stdout).
        :param err: поток для сообщений об ошибках (по умолчанию stderr).
        """
        self.vfs = vfs if vfs is not None else Vfs(DEFAULT_VFS_NAME)
        self.cwd = "/"
        self.out = out if out is not None else sys.stdout
        self.err = err if err is not None else sys.stderr

    @property
    def vfs_name(self):
        """Имя текущей VFS."""
        return self.vfs.name

    def prompt(self):
        """Вернуть приглашение к вводу, содержащее имя VFS."""
        return f"{self.vfs_name}:{self.cwd}$ "

    def write(self, text):
        """Вывести строку ``text`` в поток обычного вывода."""
        print(text, file=self.out, flush=True)

    def error(self, text):
        """Вывести сообщение об ошибке ``text``."""
        print(f"{SHELL_NAME}: {text}", file=self.err, flush=True)

    def execute(self, line):
        """Выполнить одну строку ввода.

        :return: ``True`` при успехе (в том числе для пустой строки),
            ``False`` при ошибке.
        :raises ExitRequest: если выполнена команда ``exit``.
        """
        parsed = parse(line)
        if parsed is None:
            return True
        name, args = parsed
        handler = COMMANDS.get(name)
        if handler is None:
            self.error(f"{name}: command not found")
            return False
        try:
            output = handler(self, args)
        except CommandError as exc:
            self.error(f"{name}: {exc}")
            return False
        if output:
            self.write(output)
        return True

    def repl(self, reader=input):
        """Запустить интерактивный цикл чтения-выполнения команд.

        :param reader: функция чтения строки с приглашением.
        :return: код возврата эмулятора.
        """
        while True:
            try:
                line = reader(self.prompt())
            except EOFError:
                self.write("exit")
                return 0
            except KeyboardInterrupt:
                self.write("")
                continue
            try:
                self.execute(line)
            except ExitRequest as request:
                return request.code
