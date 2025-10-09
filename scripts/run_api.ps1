Param(
  [int]$Port = 8000
)
$ErrorActionPreference = "Stop"
& "$PSScriptRoot\..\.venv\Scripts\Activate.ps1"
uvicorn src.api.main:app --host 0.0.0.0 --port $Port --reload

