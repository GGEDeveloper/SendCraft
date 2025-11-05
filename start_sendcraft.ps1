# PowerShell script para iniciar SendCraft no WSL
# Este script deve ser executado no Windows PowerShell

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SendCraft - Iniciando servidor de desenvolvimento" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se WSL está disponível
try {
    $wslStatus = wsl --status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "WSL não está disponível"
    }
} catch {
    Write-Host "ERRO: WSL não está disponível ou instalado" -ForegroundColor Red
    Write-Host "Por favor, instale o WSL primeiro" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "Conectando ao WSL e iniciando SendCraft..." -ForegroundColor Green
Write-Host ""

# Executar no WSL
# Usa a distribuição padrão do WSL
wsl -e bash -c "cd /home/ggedeveloper/SendCraft && source venv/bin/activate && python3 run_dev.py"

# Se o script terminar, manter a janela aberta
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SendCraft foi encerrado" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Read-Host "Pressione Enter para fechar"

