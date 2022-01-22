# vnv, the little shortcut for virtualenv.
# Wrapper script for PowerShell.

$VNV_FINISH = $env:USERPROFILE + "/.vnv-finish.ps1"
vnv.cli powershell $Args
if ($? -and (Test-Path -LiteralPath $VNV_FINISH -PathType Leaf)) {
    & $VNV_FINISH
    Remove-Item $VNV_FINISH
}
