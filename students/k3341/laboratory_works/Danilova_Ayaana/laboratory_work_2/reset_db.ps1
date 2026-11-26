Set-Location -Path $PSScriptRoot

if (-not (Test-Path "manage.py")) {
    Write-Host "Error: manage.py not found! Put this script in the Django project root." -ForegroundColor Red
    exit 1
}

Write-Host "=== 1. Cleaning migrations folders ===" -ForegroundColor Yellow

$migrationDirs = Get-ChildItem -Path $PSScriptRoot -Directory -Recurse -Filter "migrations" |
    Where-Object { $_.FullName -notmatch "\\(\.venv|venv|env|node_modules|\.git)\\" }

foreach ($dir in $migrationDirs) {
    $appName = $dir.Parent.Name
    Write-Host " -> Cleaning migrations in [$appName]..." -ForegroundColor Cyan
    
    Get-ChildItem -Path $dir.FullName -Filter "*.py" |
        Where-Object { $_.Name -ne "__init__.py" } |
        Remove-Item -Force

    $pycache = Join-Path $dir.FullName "__pycache__"
    if (Test-Path $pycache) {
        Remove-Item -Path $pycache -Recurse -Force
    }
}

Write-Host "`n=== 2. Resetting Database ===" -ForegroundColor Yellow

$pythonResetCode = @"
import os
from django.db import connection
from django.conf import settings

if connection.vendor == 'postgresql':
    with connection.cursor() as cursor:
        cursor.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
    print(' -> PostgreSQL database cleared (schema public recreated).')
elif connection.vendor == 'sqlite':
    db_path = settings.DATABASES['default']['NAME']
    connection.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    print(' -> SQLite database file removed.')
else:
    print(f' -> Warning: unknown DB vendor ({connection.vendor}).')
"@

python manage.py shell -c $pythonResetCode

Write-Host "`n=== 3. Making and applying new migrations ===" -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

Write-Host "`nDone! Database and migrations are completely fresh." -ForegroundColor Green