"""Точка входа: ``python -m shell_emulator [--vfs PATH] [--script PATH]``."""

import sys

from shell_emulator.config import parse_args
from shell_emulator.script import read_script, run_lines
from shell_emulator.shell import Shell

EXIT_SCRIPT_ERROR = 1
EXIT_USAGE_ERROR = 2


def run_startup_script(shell, path):
    """Выполнить стартовый скрипт.

    :return: код завершения эмулятора или ``None``, если после скрипта
        нужно перейти в интерактивный режим.
    """
    try:
        lines = read_script(path)
    except OSError as exc:
        shell.error(f"cannot open startup script: {exc}")
        return EXIT_USAGE_ERROR
    result = run_lines(shell, lines, name=path)
    if not result.ok:
        return EXIT_SCRIPT_ERROR
    return result.exit_code


def main(argv=None):
    """Разобрать параметры, выполнить скрипт и запустить REPL."""
    config = parse_args(argv)
    shell = Shell(vfs_name=config.vfs_name)
    for line in config.debug_lines():
        shell.write(line)
    if config.script_path:
        code = run_startup_script(shell, config.script_path)
        if code is not None:
            return code
    return shell.repl()


if __name__ == "__main__":
    sys.exit(main())
