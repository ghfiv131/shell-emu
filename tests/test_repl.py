"""Тесты команд и цикла REPL."""

import unittest

from tests.helpers import feeder, make_shell


class CommandsTest(unittest.TestCase):
    """Команды-заглушки и обработка ошибок."""

    def test_prompt_contains_vfs_name(self):
        """Приглашение содержит имя VFS."""
        shell, _, _ = make_shell(vfs_name="myfs")
        self.assertIn("myfs", shell.prompt())

    def test_ls_stub(self):
        """ls выводит своё имя и аргументы."""
        shell, out, _ = make_shell()
        self.assertTrue(shell.execute("ls -l /home"))
        self.assertEqual(out.getvalue(), "ls: args=['-l', '/home']\n")

    def test_cd_stub(self):
        """cd выводит своё имя и аргументы."""
        shell, out, _ = make_shell()
        self.assertTrue(shell.execute("cd /tmp"))
        self.assertEqual(out.getvalue(), "cd: args=['/tmp']\n")

    def test_unknown_command(self):
        """Неизвестная команда - ошибка."""
        shell, _, err = make_shell()
        self.assertFalse(shell.execute("foo bar"))
        self.assertIn("foo: command not found", err.getvalue())

    def test_empty_line(self):
        """Пустая строка не является ошибкой."""
        shell, out, _ = make_shell()
        self.assertTrue(shell.execute("   "))
        self.assertEqual(out.getvalue(), "")


class ExitTest(unittest.TestCase):
    """Команда exit и завершение REPL."""

    def test_exit_default(self):
        """exit без аргументов завершает с кодом 0."""
        shell, _, _ = make_shell()
        self.assertEqual(shell.repl(feeder(["ls", "exit", "ls"])), 0)

    def test_exit_code(self):
        """exit N завершает с кодом N."""
        shell, _, _ = make_shell()
        self.assertEqual(shell.repl(feeder(["exit 3"])), 3)

    def test_exit_bad_argument(self):
        """Нечисловой аргумент exit - ошибка, работа продолжается."""
        shell, _, err = make_shell()
        code = shell.repl(feeder(["exit abc", "exit 1 2", "exit 5"]))
        self.assertEqual(code, 5)
        self.assertIn("numeric argument required", err.getvalue())
        self.assertIn("too many arguments", err.getvalue())

    def test_eof(self):
        """Конец ввода (Ctrl+D) завершает работу с кодом 0."""
        shell, out, _ = make_shell()
        self.assertEqual(shell.repl(feeder([])), 0)
        self.assertIn("exit", out.getvalue())


if __name__ == "__main__":
    unittest.main()
