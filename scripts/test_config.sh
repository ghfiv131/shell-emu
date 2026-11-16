#!/usr/bin/env sh
# Этап 2: все комбинации параметров --vfs и --script.
. "$(dirname "$0")/common.sh"

run "без параметров (имя VFS по умолчанию)"
run "только --vfs" --vfs "$ROOT/vfs/minimal.json"
run "только --script" --script "$ROOT/startup/stage2_ok.txt"
run "--vfs и --script" \
    --vfs "$ROOT/vfs/minimal.json" --script "$ROOT/startup/stage2_ok.txt"
run "--script и --vfs в обратном порядке" \
    --script "$ROOT/startup/stage2_ok.txt" --vfs /opt/data/my_disk.json
run "скрипт без exit: переход в REPL (stdin пуст)" \
    --vfs /tmp/demo.json --script "$ROOT/startup/stage2_to_repl.txt"
