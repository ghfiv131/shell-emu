"""Тесты виртуальной файловой системы и служебных команд."""

import json
import os
import tempfile
import unittest

from tests.helpers import make_shell
from shell_emulator.vfs import VfsDir, VfsError, VfsFile, load_vfs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VFS_DIR = os.path.join(ROOT, "vfs")


def vfs_path(name):
    """Путь к тестовой VFS ``name``."""
    return os.path.join(VFS_DIR, name)


class LoadTest(unittest.TestCase):
    """Загрузка VFS из JSON."""

    def test_minimal(self):
        """Минимальная VFS - пустой корневой каталог."""
        vfs = load_vfs(vfs_path("minimal.json"))
        self.assertEqual(vfs.name, "minimal")
        self.assertEqual(vfs.stats(), (1, 0, 0))

    def test_multi_files_base64(self):
        """Двоичные данные декодируются из base64."""
        vfs = load_vfs(vfs_path("multi_files.json"))
        _, node = vfs.resolve("/data.bin")
        self.assertIsInstance(node, VfsFile)
        self.assertEqual(node.data, bytes(range(16)))

    def test_deep_levels(self):
        """Глубокая VFS содержит не менее трёх уровней."""
        vfs = load_vfs(vfs_path("deep.json"))
        path = "/home/user/documents/projects/shell/main.py"
        _, node = vfs.resolve(path)
        self.assertEqual(node.data, b"print('hello')\n")

    def test_name_from_file(self):
        """Без поля name имя берётся из имени файла."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "my_disk.json")
            with open(path, "w", encoding="utf-8") as file:
                json.dump({"root": {"type": "dir"}}, file)
            self.assertEqual(load_vfs(path).name, "my_disk")

    def test_file_not_modified(self):
        """Загрузка не изменяет исходный файл."""
        path = vfs_path("deep.json")
        with open(path, "rb") as file:
            before = file.read()
        load_vfs(path)
        with open(path, "rb") as file:
            self.assertEqual(file.read(), before)

    def test_invalid_files(self):
        """Некорректные файлы VFS вызывают VfsError."""
        names = ["broken_json", "no_root", "root_is_file", "bad_type",
                 "bad_base64", "bad_name"]
        for name in names:
            with self.subTest(name=name):
                with self.assertRaises(VfsError):
                    load_vfs(vfs_path(f"invalid/{name}.json"))

    def test_missing_file(self):
        """Отсутствующий файл вызывает VfsError."""
        with self.assertRaises(VfsError):
            load_vfs(vfs_path("missing.json"))


class ResolveTest(unittest.TestCase):
    """Поиск узлов по пути."""

    def setUp(self):
        """Загрузить глубокую VFS."""
        self.vfs = load_vfs(vfs_path("deep.json"))

    def test_relative_and_dots(self):
        """Относительные пути, ``.`` и ``..``."""
        path, node = self.vfs.resolve("../var/./log", "/home")
        self.assertEqual(path, "/var/log")
        self.assertIsInstance(node, VfsDir)

    def test_above_root(self):
        """``..`` выше корня остаётся в корне."""
        path, node = self.vfs.resolve("/../../")
        self.assertEqual(path, "/")
        self.assertIs(node, self.vfs.root)

    def test_not_found(self):
        """Несуществующий путь и путь через файл."""
        for path in ("/nope", "/etc/hostname/x"):
            with self.subTest(path=path):
                with self.assertRaises(VfsError):
                    self.vfs.resolve(path)


class ServiceCommandsTest(unittest.TestCase):
    """Служебные команды vfs-info и vfs-tree."""

    def setUp(self):
        """Создать оболочку с глубокой VFS."""
        vfs = load_vfs(vfs_path("deep.json"))
        self.shell, self.out, self.err = make_shell(vfs=vfs)

    def test_prompt(self):
        """Приглашение содержит имя VFS из JSON."""
        self.assertTrue(self.shell.prompt().startswith("deep:"))

    def test_info(self):
        """vfs-info выводит имя и число файлов."""
        self.assertTrue(self.shell.execute("vfs-info"))
        self.assertIn("name:        deep", self.out.getvalue())
        self.assertIn("files:       8", self.out.getvalue())

    def test_tree(self):
        """vfs-tree выводит дерево каталога."""
        self.assertTrue(self.shell.execute("vfs-tree /home/user/pictures"))
        self.assertEqual(
            self.out.getvalue(),
            "/home/user/pictures\n└── pixel.png (70 B)\n",
        )

    def test_tree_errors(self):
        """Ошибки vfs-tree и vfs-info."""
        commands = ["vfs-tree /nope", "vfs-tree /etc/motd",
                    "vfs-tree a b", "vfs-info x"]
        for command in commands:
            with self.subTest(command=command):
                self.assertFalse(self.shell.execute(command))
        errors = self.err.getvalue()
        self.assertIn("No such file or directory", errors)
        self.assertIn("Not a directory", errors)
        self.assertIn("too many arguments", errors)


if __name__ == "__main__":
    unittest.main()
