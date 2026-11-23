"""Manage an isolated local PostgreSQL cluster; never touch system clusters."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
env = root / '.env'
if env.exists():
    for line in env.read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip().strip('\"\''))
local = root / '.local'
data = local / 'postgres'
local.mkdir(exist_ok=True)

def binary(name):
    found = shutil.which(name)
    if found:
        return found
    for prefix in ['/opt/homebrew/opt/postgresql@18/bin', '/usr/lib/postgresql/18/bin', '/usr/lib/postgresql/17/bin', '/usr/lib/postgresql/16/bin']:
        candidate = Path(prefix) / name
        if candidate.exists():
            return str(candidate)
    raise SystemExit(f'{name} not found. Install PostgreSQL or use compose.yaml.')

def run(name, *args, **kwargs):
    return subprocess.run([binary(name), *map(str, args)], check=True, **kwargs)

port = os.environ.get('POSTGRES_PORT', '55432')
user = os.environ.get('POSTGRES_USER', 'flightboard')
database = os.environ.get('POSTGRES_DB', 'flightboard')
password = os.environ.get('POSTGRES_PASSWORD', 'flightboard-local')
if sys.argv[1:] == ['stop']:
    run('pg_ctl', '-D', data, '-m', 'fast', 'stop')
    sys.exit()
if not (data / 'PG_VERSION').exists():
    password_file = local / 'init-password'
    password_file.write_text(password + '\n')
    password_file.chmod(0o600)
    try:
        run('initdb', '-D', data, '-U', user, '--encoding=UTF8', '--locale=C',
            '--auth-local=trust', '--auth-host=scram-sha-256', '--pwfile', password_file)
    finally:
        password_file.unlink(missing_ok=True)
status = subprocess.run([binary('pg_ctl'), '-D', str(data), 'status'], capture_output=True)
if status.returncode:
    run('pg_ctl', '-D', data, '-l', local / 'postgres.log', '-o',
        f'-h 127.0.0.1 -p {int(port)} -k {local}', '-w', 'start')
connection_env = os.environ.copy()
connection_env['PGPASSWORD'] = password
result = run('psql', '-h', '127.0.0.1', '-p', port, '-U', user, '-d', 'postgres',
             '-tAc', 'SELECT datname FROM pg_database', capture_output=True, text=True, env=connection_env)
if database not in result.stdout.splitlines():
    run('createdb', '-h', '127.0.0.1', '-p', port, '-U', user, database, env=connection_env)
print(f'Local PostgreSQL ready on 127.0.0.1:{port}; database {database}.')
