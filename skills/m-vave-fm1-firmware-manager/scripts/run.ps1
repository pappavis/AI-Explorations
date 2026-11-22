# Version: 1.6.0 | Release ChatID: A61E4C92
param([Parameter(Position=0)][ValidateSet('start','status','refresh','update','update-all','alles')][string]$Action='start',[Parameter(ValueFromRemainingArguments=$true)][string[]]$Options)
$script=Join-Path $PSScriptRoot 'fm1_update.py'
$mode=switch($Action){ {$_ -in 'start','status'} {'status'} 'refresh' {'refresh'} default {'update-all'} }
if ($Action -eq 'status' -and $Options.Count -gt 0 -and $Options[0] -eq 'full') {
    $Options = @('--status-full') + @($Options | Select-Object -Skip 1)
}
& python $script --mode $mode @Options
exit $LASTEXITCODE
