param(
    [string]$OutputRoot
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputRoot) {
    $OutputRoot = Join-Path $projectRoot "dist"
}

$outputRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$packageRoot = Join-Path $outputRoot "Notes"
$toolsRoot = Join-Path $packageRoot "tools"

if (Test-Path -LiteralPath $packageRoot) {
    Remove-Item -LiteralPath $packageRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $packageRoot -Force | Out-Null
New-Item -ItemType Directory -Path $toolsRoot -Force | Out-Null

$repoFiles = @(
    "README.md",
    "LICENSE",
    "ARCHITECTURE.md",
    "INPUT_MAPPING.md",
    "KNOWN_LIMITATIONS.md",
    "config.json",
    "icon.png",
    "iconsel.png",
    "launch.sh",
    "notes.gptk",
    "notes_app.py"
)

foreach ($name in $repoFiles) {
    Copy-Item -LiteralPath (Join-Path $projectRoot $name) -Destination (Join-Path $packageRoot $name) -Force
}

Copy-Item -LiteralPath (Join-Path $projectRoot "notes") -Destination $packageRoot -Recurse -Force
if (Test-Path -LiteralPath (Join-Path $projectRoot "assets")) {
    Copy-Item -LiteralPath (Join-Path $projectRoot "assets") -Destination $packageRoot -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot "tools\install_to_sd.ps1") -Destination (Join-Path $toolsRoot "install_to_sd.ps1") -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "tools\run_desktop.ps1") -Destination (Join-Path $toolsRoot "run_desktop.ps1") -Force

Get-ChildItem -Path $packageRoot -Recurse -Force | Where-Object { $_.PSIsContainer -and $_.Name -eq "__pycache__" } | Remove-Item -Recurse -Force
Get-ChildItem -Path $packageRoot -Recurse -Force | Where-Object { -not $_.PSIsContainer -and $_.Extension -eq ".pyc" } | Remove-Item -Force

$zipPath = Join-Path $outputRoot "Notes-release.zip"
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path $packageRoot -DestinationPath $zipPath -CompressionLevel Optimal

Write-Host "Built release folder: $packageRoot"
Write-Host "Built release zip: $zipPath"
