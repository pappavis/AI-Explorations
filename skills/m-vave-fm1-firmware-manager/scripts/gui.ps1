# Version: 1.5.0 | Release ChatID: B6D9A420
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
python (Join-Path $here 'firmware_gui.py')
exit $LASTEXITCODE
