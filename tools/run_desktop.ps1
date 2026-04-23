param(
    [string]$Python = "auto",
    [string]$NotesDir,
    [int]$WindowScale = 2,
    [string]$FontUi,
    [string]$FontMono,
    [string]$SdlExlibs,
    [string]$SdlDllPath,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Resolve-PythonCommand {
    param([string]$CommandName)

    if ($CommandName -ne "auto") {
        return $CommandName
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }

    return "python"
}

function Assert-OptionalPathExists {
    param(
        [string]$Label,
        [string]$PathValue
    )

    if ($PathValue -and -not (Test-Path -LiteralPath $PathValue)) {
        throw "$Label was not found: $PathValue"
    }
}

$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $NotesDir) {
    $NotesDir = Join-Path $projectRoot "data\desktop-preview"
}

$Python = Resolve-PythonCommand $Python

$env:NOTES_DIR = $NotesDir
$env:NOTES_WINDOW_MODE = "windowed"
$env:NOTES_WINDOW_SCALE = [string]([Math]::Max(1, [Math]::Min(6, $WindowScale)))

if ($FontUi) {
    $env:NOTES_FONT_UI = $FontUi
}
if ($FontMono) {
    $env:NOTES_FONT_MONO = $FontMono
}
if ($SdlExlibs) {
    $env:NOTES_SDL_EXLIBS = $SdlExlibs
}
if ($SdlDllPath) {
    $env:NOTES_SDL_DLL_PATH = $SdlDllPath
}

Assert-OptionalPathExists "NotesDir parent" (Split-Path -Parent $env:NOTES_DIR)
Assert-OptionalPathExists "FontUi" $FontUi
Assert-OptionalPathExists "FontMono" $FontMono
Assert-OptionalPathExists "SdlExlibs" $SdlExlibs
Assert-OptionalPathExists "SdlDllPath" $SdlDllPath

Write-Host "NOTES_DIR=$($env:NOTES_DIR)"
Write-Host "NOTES_WINDOW_MODE=$($env:NOTES_WINDOW_MODE)"
Write-Host "NOTES_WINDOW_SCALE=$($env:NOTES_WINDOW_SCALE)"
Write-Host "PYTHON=$Python"

if ($DryRun) {
    Write-Host "Desktop launcher dry-run completed"
    exit 0
}

Push-Location $projectRoot
try {
    & $Python "notes_app.py"
}
finally {
    Pop-Location
}
