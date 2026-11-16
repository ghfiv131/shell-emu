#!/usr/bin/env sh
# Запуск эмулятора: ./run.sh [параметры]
# Запуск тестов:    ./run.sh test
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
if [ "$1" = "test" ]; then
    exec python3 -m unittest discover -s "$ROOT/tests" -v
fi
exec python3 -m shell_emulator "$@"
