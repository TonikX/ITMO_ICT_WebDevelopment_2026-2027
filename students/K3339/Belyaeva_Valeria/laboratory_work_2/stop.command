#!/bin/zsh
set -e
cd "${0:A:h}"
export PATH="/opt/homebrew/opt/postgresql@16/bin:/usr/local/opt/postgresql@16/bin:$PATH"
pg_ctl -D .runtime/postgres stop
