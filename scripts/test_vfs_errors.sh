#!/usr/bin/env sh
# Этап 3: ошибки загрузки VFS (эмулятор завершается с кодом 2).
. "$(dirname "$0")/common.sh"

SCRIPT="$ROOT/startup/stage3_vfs.txt"
run "файл VFS не существует" --vfs "$ROOT/vfs/missing.json" \
    --script "$SCRIPT"
run "путь VFS - каталог" --vfs "$ROOT/vfs" --script "$SCRIPT"
for name in broken_json no_root root_is_file bad_type bad_base64 \
        bad_name; do
    run "некорректная VFS: $name" \
        --vfs "$ROOT/vfs/invalid/$name.json" --script "$SCRIPT"
done
