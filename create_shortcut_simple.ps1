# Simple PowerShell script to create shortcut
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$TargetPath = Join-Path -Path $PWD -ChildPath "antivirus_agent_ai.py"
$PythonPath = (Get-Command python).Source

# Check if target file exists
if (-not (Test-Path $TargetPath)) {
    Write-Host "ERROR: Target file not found: $TargetPath"
    exit 1
}

# Create shortcut
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\AntivirusAgent.lnk")
    $Shortcut.TargetPath = $PythonPath
    $Shortcut.Arguments = "`"$TargetPath`""
    $Shortcut.WorkingDirectory = $PWD.Path
    $Shortcut.Description = "Antivirus Agent AI"
    $Shortcut.Save()
    
    Write-Host "SUCCESS: Shortcut created: $DesktopPath\AntivirusAgent.lnk"
    Write-Host "Python path: $PythonPath"
    Write-Host "Target file: $TargetPath"
    exit 0
}
catch {
    Write-Host "ERROR: $_"
    exit 1
}
