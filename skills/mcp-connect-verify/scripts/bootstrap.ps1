$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Cache = Join-Path $env:LOCALAPPDATA 'mcp-connect-verify'
$Python = $null
foreach ($Candidate in @('python', 'python3')) {
    if (Get-Command $Candidate -ErrorAction SilentlyContinue) {
        & $Candidate -c 'import sys; assert sys.version_info >= (3,11)' 2>$null
        if ($LASTEXITCODE -eq 0) { $Python = $Candidate; break }
    }
}
if (-not $Python) {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        & uv python install 3.12
        if ($LASTEXITCODE -ne 0) { throw 'Python installation failed' }
        $Python = (& uv python find 3.12).Trim()
    } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
        & winget install --id Python.Python.3.12 --exact --scope user --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) { throw 'Python installation failed' }
        $Python = Join-Path $env:LOCALAPPDATA 'Programs/Python/Python312/python.exe'
        if (-not (Test-Path $Python)) { throw 'Find the installed Python executable and rerun the bootstrap' }
    } else { throw 'Python >=3.11 ontbreekt. Gebruik de officiële OS-pakketbeheerder; vraag alleen benodigde systeemtoestemming.' }
}
$VenvPython = Join-Path $Cache 'venv/Scripts/python.exe'
if (-not (Test-Path $VenvPython)) {
    & $Python -m venv (Join-Path $Cache 'venv')
    if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
}
$Requirements = Join-Path $PSScriptRoot 'requirements.txt'
$Fingerprint = (Get-FileHash $Requirements -Algorithm SHA256).Hash
$Stamp = Join-Path $Cache 'requirements.sha256'
if (-not (Test-Path $Stamp) -or (Get-Content $Stamp -Raw).Trim() -ne $Fingerprint) {
    & $VenvPython -m pip --disable-pip-version-check install -r $Requirements
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
    Set-Content $Stamp $Fingerprint
}
& $VenvPython (Join-Path $PSScriptRoot 'mcp_manager.py') @args
exit $LASTEXITCODE
