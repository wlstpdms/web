param(
    [Parameter(Mandatory = $true)][string]$NginxRoot,
    [Parameter(Mandatory = $true)][string]$DistPath
)

$ErrorActionPreference = 'Stop'
$NginxRoot = (Resolve-Path -LiteralPath $NginxRoot).Path
$DistPath = (Resolve-Path -LiteralPath $DistPath).Path
$nginxExe = Join-Path $NginxRoot 'nginx.exe'
$configPath = Join-Path $NginxRoot 'conf\nginx.conf'
$candidatePath = Join-Path $NginxRoot 'conf\nginx.login-fix.conf'
$builtConfig = Join-Path (Split-Path -Parent $DistPath) 'nginx.conf'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $NginxRoot "login-fix-backup-$stamp"
if (!(Test-Path -LiteralPath $nginxExe) -or !(Test-Path -LiteralPath (Join-Path $DistPath 'index.html'))) {
    throw 'nginx.exe or built frontend index.html is missing.'
}
if (!(Test-Path -LiteralPath $builtConfig)) {
    throw 'Generated nginx.conf must be alongside dist. Run npm run build and copy both outputs.'
}

New-Item -ItemType Directory -Path $backupRoot | Out-Null
Copy-Item -LiteralPath $configPath -Destination (Join-Path $backupRoot 'nginx.conf')
Copy-Item -LiteralPath (Join-Path $NginxRoot 'html') -Destination (Join-Path $backupRoot 'html') -Recurse
Copy-Item -LiteralPath $builtConfig -Destination $candidatePath

Push-Location -LiteralPath $NginxRoot
try {
    & $nginxExe -p "$NginxRoot/" -c 'conf/nginx.login-fix.conf' -t
    if ($LASTEXITCODE -ne 0) { throw 'nginx validation failed; active config was not replaced.' }
    # Copy assets first and entry HTML last. Retain old hashed assets for open tabs.
    Copy-Item -Path (Join-Path $DistPath 'assets\*') -Destination (Join-Path $NginxRoot 'html\assets') -Recurse -Force
    Get-ChildItem -LiteralPath $DistPath -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $NginxRoot 'html') -Force
    }
    Copy-Item -LiteralPath $candidatePath -Destination $configPath -Force
    & $nginxExe -p "$NginxRoot/" -t
    if ($LASTEXITCODE -ne 0) { throw 'nginx active configuration validation failed.' }
    # Several manual launches can leave multiple masters sharing port 80.
    # Reload each master belonging to this installation, not only nginx.pid.
    $processes = @(Get-CimInstance Win32_Process -Filter "Name='nginx.exe'" |
        Where-Object { $_.ExecutablePath -eq $nginxExe })
    $processIds = @($processes.ProcessId)
    $reloaded = 0
    foreach ($process in $processes) {
        if ($process.ParentProcessId -in $processIds) { continue }
        $signalPidPath = "logs/nginx.reload-$($process.ProcessId).pid"
        [IO.File]::WriteAllText((Join-Path $NginxRoot $signalPidPath), [string]$process.ProcessId)
        & $nginxExe -p "$NginxRoot/" -g "pid $signalPidPath;" -s reload
        if ($LASTEXITCODE -eq 0) {
            $reloaded++
        } else {
            Write-Warning "Process $($process.ProcessId) could not reload; inspect for an orphan worker."
        }
    }
    if ($reloaded -eq 0) { throw 'No running nginx master accepted the reload.' }
    Write-Output "Applied frontend and nginx configuration. Backup: $backupRoot"
} catch {
    Copy-Item -LiteralPath (Join-Path $backupRoot 'nginx.conf') -Destination $configPath -Force
    throw
} finally {
    Pop-Location
}
