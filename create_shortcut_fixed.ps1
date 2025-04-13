$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$TargetPath = Join-Path -Path $PWD -ChildPath "antivirus_agent_ai.py"
$PythonPath = (Get-Command python).Source

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\AntivirusAgent.lnk")
$Shortcut.TargetPath = $PythonPath
$Shortcut.Arguments = "`"$TargetPath`""
$Shortcut.WorkingDirectory = $PWD.Path
$Shortcut.Description = "Antivirus Agent AI"
$Shortcut.Save()

Write-Host "Skrót został utworzony: $DesktopPath\AntivirusAgent.lnk"
Write-Host "Cel: $PythonPath `"$TargetPath`""
