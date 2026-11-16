#!/usr/bin/env sh
# Этап 3: работа с различными вариантами VFS.
. "$(dirname "$0")/common.sh"

run "пустая VFS в памяти (без --vfs)" \
    --script "$ROOT/startup/stage3_vfs.txt"
run "минимальная VFS (только корень)" \
    --vfs "$ROOT/vfs/minimal.json" --script "$ROOT/startup/stage3_vfs.txt"
run "VFS с несколькими файлами (текст и base64)" \
    --vfs "$ROOT/vfs/multi_files.json" \
    --script "$ROOT/startup/stage3_vfs.txt"
run "VFS с 3+ уровнями файлов и папок" \
    --vfs "$ROOT/vfs/deep.json" --script "$ROOT/startup/stage3_vfs.txt"
run "все команды этапов 1-3 на глубокой VFS" \
    --vfs "$ROOT/vfs/deep.json" --script "$ROOT/startup/stage3_all.txt"
run "ошибка: файл вместо каталога" \
    --vfs "$ROOT/vfs/deep.json" --script "$ROOT/startup/stage3_not_dir.txt"
run "ошибка: лишний аргумент служебной команды" \
    --vfs "$ROOT/vfs/minimal.json" --script "$ROOT/startup/stage3_args.txt"
