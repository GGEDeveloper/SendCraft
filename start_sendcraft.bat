@echo off
REM Script para iniciar SendCraft no WSL a partir do Windows
REM Este script deve ser executado no Windows (não no WSL)

title SendCraft Development Server

echo ============================================
echo SendCraft - Iniciando servidor de desenvolvimento
echo ============================================
echo.

REM Verificar se WSL está disponível
wsl --status >nul 2>&1
if errorlevel 1 (
    echo ERRO: WSL nao esta disponivel ou instalado
    echo Por favor, instale o WSL primeiro
    pause
    exit /b 1
)

echo Verificando distribuição WSL...
for /f "tokens=*" %%i in ('wsl --list --quiet') do (
    set WSL_DISTRO=%%i
    goto :found_distro
)
:found_distro

echo Distribuição WSL: %WSL_DISTRO%
echo.
echo Conectando ao WSL e iniciando SendCraft...
echo Caminho: /home/ggedeveloper/SendCraft
echo.

REM Executar no WSL
REM Usa a distribuição padrão do WSL
wsl -e bash -c "cd /home/ggedeveloper/SendCraft && source venv/bin/activate && python3 run_dev.py"

REM Se o script terminar, manter a janela aberta
echo.
echo ============================================
echo SendCraft foi encerrado
echo ============================================
pause

