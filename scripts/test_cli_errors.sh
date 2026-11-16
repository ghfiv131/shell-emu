#!/usr/bin/env sh
# Этап 2: справка и ошибки в параметрах командной строки.
. "$(dirname "$0")/common.sh"

run "справка" --help
run "у --vfs нет значения" --vfs
run "у --script нет значения" --vfs /tmp/a.json --script
run "неизвестный параметр" --vfs /tmp/a.json --unknown
