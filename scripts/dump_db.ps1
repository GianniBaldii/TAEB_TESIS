param(
    [string]$DumpFile
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$DumpDir = Join-Path $RepoRoot "docker\mysql\dumps"

if (-not $DumpFile) {
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $DumpFile = "taeb_backup_pruebas_$Timestamp.sql"
}

if ([System.IO.Path]::IsPathRooted($DumpFile)) {
    $DumpPath = $DumpFile
} else {
    $DumpPath = Join-Path $DumpDir $DumpFile
}

New-Item -ItemType Directory -Force $DumpDir | Out-Null

Push-Location $RepoRoot
try {
    $DumpCommand = 'export MYSQL_PWD="$MYSQL_PASSWORD"; exec mysqldump --single-transaction --routines --triggers --events --hex-blob --no-tablespaces -u"$MYSQL_USER" "$MYSQL_DATABASE"'
    docker compose exec -T db sh -c $DumpCommand | Set-Content -Path $DumpPath -Encoding UTF8
    Write-Host "Dump creado en $DumpPath"
} finally {
    Pop-Location
}
