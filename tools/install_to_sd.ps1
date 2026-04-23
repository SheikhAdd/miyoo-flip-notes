param(
    [Parameter(Mandatory = $true)]
    [string]$Drive
)

$ErrorActionPreference = "Stop"

function Resolve-SdRoot {
    param([string]$DriveValue)

    $value = $DriveValue.Trim()
    if ($value -match "^[A-Za-z]$") {
        $value = "$value`:"
    }
    if ($value -match "^[A-Za-z]:$") {
        $value = "$value\"
    }
    if ($value -notmatch "^[A-Za-z]:\\$") {
        throw "Drive must look like X: or X:\"
    }
    return $value
}

function Copy-HelperFile {
    param(
        [string]$SdRoot,
        [string]$TargetRoot,
        [string]$Name,
        [string[]]$Candidates
    )

    foreach ($relativePath in $Candidates) {
        $candidate = Join-Path $SdRoot $relativePath
        if (Test-Path -LiteralPath $candidate) {
            Copy-Item -LiteralPath $candidate -Destination (Join-Path $TargetRoot $Name) -Force
            return $candidate
        }
    }

    $list = $Candidates -join ", "
    throw "Could not find $Name on the SD card. Checked: $list"
}

$sdRoot = Resolve-SdRoot $Drive
$projectRoot = Split-Path -Parent $PSScriptRoot
$appRoot = Join-Path $sdRoot "App"
$dataRoot = Join-Path $sdRoot "Data"
$targetRoot = Join-Path $appRoot "Notes"

if (-not (Test-Path -LiteralPath $appRoot)) {
    throw "App folder was not found under $sdRoot. This does not look like a Surwish OS SD card."
}

New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $dataRoot "Notes") -Force | Out-Null

$runtimeFiles = @(
    "config.json",
    "icon.png",
    "iconsel.png",
    "launch.sh",
    "notes.gptk",
    "notes_app.py"
)

foreach ($name in $runtimeFiles) {
    Copy-Item -LiteralPath (Join-Path $projectRoot $name) -Destination (Join-Path $targetRoot $name) -Force
}

$targetNotes = Join-Path $targetRoot "notes"
if (Test-Path -LiteralPath $targetNotes) {
    Remove-Item -LiteralPath $targetNotes -Recurse -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot "notes") -Destination $targetRoot -Recurse -Force

$gptokeybSource = Copy-HelperFile -SdRoot $sdRoot -TargetRoot $targetRoot -Name "gptokeyb" -Candidates @(
    "App\\PixelReader\\gptokeyb",
    "App\\RTC\\gptokeyb",
    "App\\PortMaster\\PortMaster\\gptokeyb"
)

$gameControllerDbSource = Copy-HelperFile -SdRoot $sdRoot -TargetRoot $targetRoot -Name "gamecontrollerdb.txt" -Candidates @(
    "App\\PortMaster\\PortMaster\\gamecontrollerdb.txt",
    "App\\PixelReader\\gamecontrollerdb.txt",
    "App\\RTC\\gamecontrollerdb.txt"
)

Write-Host "Installed Notes to $targetRoot"
Write-Host "Copied gptokeyb from $gptokeybSource"
Write-Host "Copied gamecontrollerdb.txt from $gameControllerDbSource"
