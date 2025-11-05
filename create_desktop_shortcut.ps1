# Script PowerShell para criar atalho no desktop do Windows
# Execute este script no PowerShell como Administrador (se necessário)

Write-Host "Criando atalho do SendCraft no desktop..." -ForegroundColor Cyan

# Obter caminho do desktop do usuário
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "SendCraft.lnk"

# Obter caminho do script atual
$scriptPath = $PSScriptRoot
$batFile = Join-Path $scriptPath "start_sendcraft.bat"

# Verificar se o arquivo .bat existe
if (-not (Test-Path $batFile)) {
    Write-Host "ERRO: Arquivo start_sendcraft.bat nao encontrado em: $scriptPath" -ForegroundColor Red
    exit 1
}

# Criar objeto Shell para criar atalho
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($shortcutPath)

# Configurar atalho
$Shortcut.TargetPath = $batFile
$Shortcut.WorkingDirectory = $scriptPath
$Shortcut.Description = "Iniciar SendCraft Development Server no WSL"
$Shortcut.IconLocation = "C:\Windows\System32\wsl.exe,0"  # Ícone do WSL

# Salvar atalho
$Shortcut.Save()

Write-Host "✅ Atalho criado com sucesso em: $shortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "O atalho 'SendCraft' foi adicionado ao seu desktop." -ForegroundColor Yellow
Write-Host "Clique duas vezes nele para iniciar o servidor de desenvolvimento." -ForegroundColor Yellow

