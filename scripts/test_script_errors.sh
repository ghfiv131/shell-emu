#!/usr/bin/env sh
# Этап 2: ошибки во время выполнения стартового скрипта.
. "$(dirname "$0")/common.sh"

run "неизвестная команда в скрипте" \
    --vfs "$ROOT/vfs/minimal.json" \
    --script "$ROOT/startup/stage2_error.txt"
run "неверный аргумент exit в скрипте" \
    --vfs "$ROOT/vfs/deep.json" --script "$ROOT/startup/stage2_exit_error.txt"
run "стартовый скрипт не существует" \
    --vfs "$ROOT/vfs/minimal.json" --script "$ROOT/startup/missing.txt"
