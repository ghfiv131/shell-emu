"""Встроенные команды эмулятора.

Каждая команда - функция ``handler(shell, args)``, которая возвращает
текст для вывода (или пустую строку) либо возбуждает
:class:`CommandError` при ошибке.
"""

MAX_EXIT_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды (выводится пользователю)."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора с кодом возврата."""

    def __init__(self, code):
        """Сохранить код возврата ``code``."""
        super().__init__(code)
        self.code = code


def _stub(name, args):
    """Сформировать вывод команды-заглушки: имя и аргументы."""
    return f"{name}: args={args!r}"


def cmd_ls(shell, args):
    """Команда ``ls`` (заглушка): вывести имя команды и аргументы."""
    return _stub("ls", args)


def cmd_cd(shell, args):
    """Команда ``cd`` (заглушка): вывести имя команды и аргументы."""
    return _stub("cd", args)


def cmd_exit(shell, args):
    """Команда ``exit [code]``: завершить работу эмулятора.

    :raises CommandError: если аргументов больше одного или код
        возврата не является целым числом.
    :raises ExitRequest: для завершения работы.
    """
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("too many arguments")
    if not args:
        raise ExitRequest(0)
    try:
        code = int(args[0])
    except ValueError:
        raise CommandError(
            f"{args[0]}: numeric argument required"
        ) from None
    raise ExitRequest(code)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
