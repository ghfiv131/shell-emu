"""Точка входа: ``python -m shell_emulator``."""

import sys

from shell_emulator.shell import Shell


def main():
    """Запустить эмулятор в интерактивном режиме."""
    return Shell().repl()


if __name__ == "__main__":
    sys.exit(main())
