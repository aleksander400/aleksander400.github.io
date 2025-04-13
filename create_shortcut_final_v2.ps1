# Skrypt do tworzenia skrótu do aplikacji antywirusowej
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$TargetPath = Join-Path -Path $PWD -ChildPath "antivirus_agent_ai.py"
$PythonPath = (Get-Command python).Source

# Sprawdzenie czy plik docelowy istnieje
if (-not (Test-Path $TargetPath)) {
    Write-Host "BŁĄD: Plik docelowy nie istnieje: $TargetPath"
    exit 1
}

# Utworzenie skrótu
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\AntivirusAgent.lnk")
    $Shortcut.TargetPath = $PythonPath
    $Shortcut.Arguments = "`"$TargetPath`""
    $Shortcut.WorkingDirectory = $PWD.Path
    $Shortcut.Description = "Antivirus Agent AI"
    $Shortcut.Save()
    
    Write-Host "SUKCES: Skrót został utworzony: $DesktopPath\AntivirusAgent.lnk"
    Write-Host "Ścieżka Pythona: $PythonPath"
    Write-Host "Plik docelowy: $TargetPath"
    exit 0
}
catch {
    Write-Host "BŁĄD: $_"
    exit 1
}
