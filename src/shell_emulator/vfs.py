"""Виртуальная файловая система (VFS), загружаемая из JSON-файла.

Формат файла::

    {
      "name": "my_disk",
      "root": {
        "type": "dir",
        "children": {
          "readme.txt": {"type": "file", "content": "text"},
          "logo.bin": {"type": "file", "encoding": "base64",
                       "content": "AAEC"},
          "home": {"type": "dir", "children": {}}
        }
      }
    }

Поле ``name`` необязательно (по умолчанию - имя файла без расширения).
Все данные хранятся только в памяти, исходный файл не изменяется.
"""

import base64
import binascii
import json
import os

TYPE_DIR = "dir"
TYPE_FILE = "file"
ENCODING_TEXT = "text"
ENCODING_BASE64 = "base64"
SEPARATOR = "/"
FORBIDDEN_NAMES = ("", ".", "..")


class VfsError(Exception):
    """Ошибка загрузки VFS или доступа к её узлам."""


class VfsFile:
    """Файл VFS с двоичным содержимым ``data``."""

    def __init__(self, name, data):
        """Создать файл с именем ``name`` и содержимым ``data`` (bytes)."""
        self.name = name
        self.data = data

    @property
    def size(self):
        """Размер файла в байтах."""
        return len(self.data)


class VfsDir:
    """Каталог VFS: словарь дочерних узлов ``children``."""

    def __init__(self, name, children=None):
        """Создать каталог ``name`` с дочерними узлами ``children``."""
        self.name = name
        self.children = children if children is not None else {}

    def sorted_children(self):
        """Вернуть дочерние узлы, отсортированные по имени."""
        return [self.children[key] for key in sorted(self.children)]


class Vfs:
    """Загруженная в память виртуальная файловая система."""

    def __init__(self, name, root=None, source=None):
        """Создать VFS с именем ``name`` и корнем ``root``.

        :param source: путь к исходному JSON-файлу (``None`` - пустая VFS).
        """
        self.name = name
        self.root = root if root is not None else VfsDir("")
        self.source = source

    def resolve(self, path, cwd=SEPARATOR):
        """Найти узел по абсолютному или относительному пути.

        :param path: путь; ``.`` и ``..`` поддерживаются.
        :param cwd: текущий каталог для относительного пути.
        :return: кортеж ``(абсолютный путь, узел)``.
        :raises VfsError: если путь не существует.
        """
        full = path if path.startswith(SEPARATOR) else f"{cwd}/{path}"
        parts = []
        for part in full.split(SEPARATOR):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(part)
        node = self.root
        for part in parts:
            if not isinstance(node, VfsDir) or part not in node.children:
                raise VfsError(f"{path}: No such file or directory")
            node = node.children[part]
        return SEPARATOR + SEPARATOR.join(parts), node

    def stats(self):
        """Вернуть ``(число каталогов, число файлов, размер в байтах)``."""
        dirs, files, size = 0, 0, 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            if isinstance(node, VfsDir):
                dirs += 1
                stack.extend(node.children.values())
            else:
                files += 1
                size += node.size
        return dirs, files, size


def tree_lines(node, prefix=""):
    """Вернуть строки псевдографического дерева потомков каталога."""
    lines = []
    children = node.sorted_children()
    for index, child in enumerate(children):
        last = index == len(children) - 1
        branch, indent = ("└── ", "    ") if last else ("├── ", "│   ")
        if isinstance(child, VfsDir):
            lines.append(f"{prefix}{branch}{child.name}/")
            lines.extend(tree_lines(child, prefix + indent))
        else:
            lines.append(f"{prefix}{branch}{child.name} ({child.size} B)")
    return lines


def _decode_content(spec, where):
    """Получить байты содержимого файла из описания ``spec``."""
    content = spec.get("content", "")
    encoding = spec.get("encoding", ENCODING_TEXT)
    if not isinstance(content, str):
        raise VfsError(f"{where}: 'content' must be a string")
    if encoding == ENCODING_TEXT:
        return content.encode("utf-8")
    if encoding == ENCODING_BASE64:
        try:
            return base64.b64decode(content, validate=True)
        except binascii.Error as exc:
            raise VfsError(f"{where}: invalid base64: {exc}") from None
    raise VfsError(f"{where}: unknown encoding {encoding!r}")


def _build_dir(name, spec, where):
    """Построить каталог VFS из описания ``spec``."""
    children = spec.get("children", {})
    if not isinstance(children, dict):
        raise VfsError(f"{where}: 'children' must be an object")
    node = VfsDir(name)
    for child_name, child_spec in children.items():
        if child_name in FORBIDDEN_NAMES or SEPARATOR in child_name:
            raise VfsError(f"{where}: invalid name {child_name!r}")
        child_where = f"{where.rstrip(SEPARATOR)}/{child_name}"
        node.children[child_name] = _build_node(
            child_name, child_spec, child_where
        )
    return node


def _build_node(name, spec, where):
    """Построить узел VFS (файл или каталог) из описания ``spec``."""
    if not isinstance(spec, dict):
        raise VfsError(f"{where}: node must be an object")
    node_type = spec.get("type")
    if node_type == TYPE_DIR:
        return _build_dir(name, spec, where)
    if node_type == TYPE_FILE:
        return VfsFile(name, _decode_content(spec, where))
    raise VfsError(f"{where}: unknown node type {node_type!r}")


def _read_json(path):
    """Прочитать и разобрать JSON-файл ``path``."""
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except OSError as exc:
        raise VfsError(f"cannot read VFS file: {exc}") from None
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise VfsError(f"{path}: invalid JSON: {exc}") from None


def default_name(path):
    """Имя VFS по умолчанию: имя файла ``path`` без расширения."""
    base = os.path.basename(os.path.normpath(path))
    return os.path.splitext(base)[0]


def load_vfs(path):
    """Загрузить VFS из JSON-файла ``path`` в память.

    :raises VfsError: если файл не читается или имеет неверный формат.
    """
    data = _read_json(path)
    if not isinstance(data, dict) or "root" not in data:
        raise VfsError(f"{path}: expected an object with 'root' key")
    name = data.get("name", default_name(path))
    if not isinstance(name, str) or not name:
        raise VfsError(f"{path}: 'name' must be a non-empty string")
    try:
        root = _build_node("", data["root"], SEPARATOR)
    except VfsError as exc:
        raise VfsError(f"{path}: {exc}") from None
    if not isinstance(root, VfsDir):
        raise VfsError(f"{path}: root must be a directory")
    return Vfs(name, root, os.path.abspath(path))
