Param(
  [Parameter(Mandatory=$true)][string]$Query
)
$ErrorActionPreference = "Stop"
& "$PSScriptRoot\..\.venv\Scripts\Activate.ps1"
python "$PSScriptRoot\..\cli.py" $Query

