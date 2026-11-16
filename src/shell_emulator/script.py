"""Выполнение стартового скрипта эмулятора."""

from dataclasses import dataclass
from typing import Optional

from shell_emulator.commands import ExitRequest

COMMENT_PREFIX = "#"


@dataclass
class ScriptResult:
    """Результат выполнения скрипта.

    :ivar ok: ``True``, если все команды выполнены без ошибок.
    :ivar exit_code: код из команды ``exit``, если она была вызвана.
    """

    ok: bool
    exit_code: Optional[int] = None


def read_script(path):
    """Прочитать скрипт ``path`` и вернуть список строк.

    :raises OSError: если файл не удаётся открыть.
    """
    with open(path, encoding="utf-8") as file:
        return file.read().splitlines()


def run_lines(shell, lines, name="script"):
    """Выполнить строки скрипта ``lines`` в оболочке ``shell``.

    Каждая команда выводится вместе с приглашением, имитируя диалог
    с пользователем. Пустые строки и строки, начинающиеся с ``#``,
    пропускаются. Выполнение останавливается при первой ошибке.

    :param name: имя скрипта для сообщения об ошибке.
    :return: :class:`ScriptResult`.
    """
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(COMMENT_PREFIX):
            continue
        shell.write(shell.prompt() + stripped)
        try:
            ok = shell.execute(stripped)
        except ExitRequest as request:
            return ScriptResult(True, request.code)
        if not ok:
            shell.error(
                f"{name}:{number}: error in command '{stripped}', "
                "script aborted"
            )
            return ScriptResult(False)
    return ScriptResult(True)
