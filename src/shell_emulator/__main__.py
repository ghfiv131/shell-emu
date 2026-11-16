"""Точка входа: ``python -m shell_emulator [--vfs PATH] [--script PATH]``."""

import sys

from shell_emulator.config import parse_args
from shell_emulator.script import read_script, run_lines
from shell_emulator.shell import Shell
from shell_emulator.vfs import Vfs, VfsError, load_vfs

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


def load_config_vfs(config):
    """Загрузить VFS по параметру ``--vfs`` или создать пустую.

    :raises VfsError: если VFS не удаётся загрузить.
    """
    if not config.vfs_path:
        return Vfs(config.vfs_name)
    return load_vfs(config.vfs_path)


def main(argv=None):
    """Разобрать параметры, загрузить VFS, выполнить скрипт и REPL."""
    config = parse_args(argv)
    shell = Shell()
    for line in config.debug_lines():
        shell.write(line)
    try:
        shell.vfs = load_config_vfs(config)
    except VfsError as exc:
        shell.error(f"cannot load VFS: {exc}")
        return EXIT_USAGE_ERROR
    dirs, files, size = shell.vfs.stats()
    shell.write(
        f"[debug] vfs loaded: name={shell.vfs_name!r}, dirs={dirs}, "
        f"files={files}, size={size}"
    )
    if config.script_path:
        code = run_startup_script(shell, config.script_path)
        if code is not None:
            return code
    return shell.repl()


if __name__ == "__main__":
    sys.exit(main())
