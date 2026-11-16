"""Встроенные команды эмулятора.

Каждая команда - функция ``handler(shell, args)``, которая возвращает
текст для вывода (или пустую строку) либо возбуждает
:class:`CommandError` при ошибке.
"""

from shell_emulator.vfs import VfsDir, VfsError, tree_lines

MAX_EXIT_ARGS = 1
MAX_TREE_ARGS = 1


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


def cmd_vfs_info(shell, args):
    """Служебная команда ``vfs-info``: сведения о загруженной VFS.

    :raises CommandError: если переданы аргументы.
    """
    if args:
        raise CommandError("too many arguments")
    vfs = shell.vfs
    dirs, files, size = vfs.stats()
    source = vfs.source or "(in-memory, empty)"
    return "\n".join([
        f"name:        {vfs.name}",
        f"source:      {source}",
        f"directories: {dirs}",
        f"files:       {files}",
        f"size:        {size} bytes",
    ])


def cmd_vfs_tree(shell, args):
    """Служебная команда ``vfs-tree [path]``: дерево каталога VFS.

    :raises CommandError: если аргументов больше одного, путь не
        существует или не является каталогом.
    """
    if len(args) > MAX_TREE_ARGS:
        raise CommandError("too many arguments")
    path = args[0] if args else shell.cwd
    try:
        full_path, node = shell.vfs.resolve(path, shell.cwd)
    except VfsError as exc:
        raise CommandError(str(exc)) from None
    if not isinstance(node, VfsDir):
        raise CommandError(f"{path}: Not a directory")
    return "\n".join([full_path] + tree_lines(node))


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
    "vfs-tree": cmd_vfs_tree,
}
