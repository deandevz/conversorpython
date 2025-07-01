@echo off
:: Remover FFmpeg do PATH do Windows
:: Use este script caso precise remover o FFmpeg do PATH

echo =====================================
echo    REMOVER FFMPEG DO PATH
echo =====================================
echo.

:: Verificar se está executando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Executando como Administrador
) else (
    echo [ERRO] Este script precisa ser executado como Administrador!
    echo.
    echo Por favor:
    echo 1. Clique com botao direito neste arquivo
    echo 2. Selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

:: Definir o caminho do FFmpeg
set "FFMPEG_PATH=C:\Program Files\ffmpeg"

echo [INFO] Removendo do PATH: %FFMPEG_PATH%
echo.

:: Obter o PATH atual do sistema
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "CURRENT_PATH=%%B"

:: Remover FFmpeg do PATH (incluindo variações com \bin)
set "NEW_PATH=%CURRENT_PATH%"
set "NEW_PATH=%NEW_PATH:;C:\Program Files\ffmpeg\bin=%"
set "NEW_PATH=%NEW_PATH:;C:\Program Files\ffmpeg=%"
set "NEW_PATH=%NEW_PATH:C:\Program Files\ffmpeg\bin;=%"
set "NEW_PATH=%NEW_PATH:C:\Program Files\ffmpeg;=%"

:: Verificar se houve mudança
if "%NEW_PATH%"=="%CURRENT_PATH%" (
    echo [INFO] FFmpeg nao estava no PATH do sistema.
    echo.
    pause
    exit /b 0
)

:: Atualizar o PATH do sistema
setx /M PATH "%NEW_PATH%" >nul 2>&1

if %errorLevel% == 0 (
    echo [OK] FFmpeg removido do PATH com sucesso!
    echo.
    echo IMPORTANTE:
    echo - Feche e reabra o Prompt de Comando
    echo - Ou reinicie o computador para aplicar as mudancas
) else (
    echo [ERRO] Falha ao remover do PATH!
    echo Tente executar novamente como Administrador.
)

echo.
pause