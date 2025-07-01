@echo off
:: Adicionar FFmpeg ao PATH do Windows
:: Este script adiciona C:\Program Files\ffmpeg ao PATH do sistema

echo =====================================
echo    ADICIONAR FFMPEG AO PATH
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

:: Verificar se o diretório existe
if not exist "%FFMPEG_PATH%" (
    echo [ERRO] Diretorio nao encontrado: %FFMPEG_PATH%
    echo.
    echo Verifique se o FFmpeg esta instalado em:
    echo %FFMPEG_PATH%
    echo.
    pause
    exit /b 1
)

:: Verificar se ffmpeg.exe existe no diretório
if not exist "%FFMPEG_PATH%\ffmpeg.exe" (
    :: Tentar subdiretório bin
    if exist "%FFMPEG_PATH%\bin\ffmpeg.exe" (
        set "FFMPEG_PATH=%FFMPEG_PATH%\bin"
        echo [INFO] FFmpeg encontrado em: %FFMPEG_PATH%
    ) else (
        echo [ERRO] ffmpeg.exe nao encontrado!
        echo.
        echo Verifique se o FFmpeg esta corretamente instalado.
        echo Procurado em:
        echo - %FFMPEG_PATH%\ffmpeg.exe
        echo - %FFMPEG_PATH%\bin\ffmpeg.exe
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Adicionando ao PATH do sistema: %FFMPEG_PATH%
echo.

:: Obter o PATH atual do sistema
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "CURRENT_PATH=%%B"

:: Verificar se já está no PATH
echo %CURRENT_PATH% | findstr /I /C:"%FFMPEG_PATH%" >nul
if %errorLevel% == 0 (
    echo [INFO] FFmpeg ja esta no PATH do sistema!
    echo.
    echo Testando ffmpeg...
    ffmpeg -version >nul 2>&1
    if %errorLevel% == 0 (
        echo [OK] FFmpeg funcionando corretamente!
    ) else (
        echo [AVISO] FFmpeg no PATH mas nao responde. Reinicie o computador.
    )
    echo.
    pause
    exit /b 0
)

:: Adicionar ao PATH do sistema
setx /M PATH "%CURRENT_PATH%;%FFMPEG_PATH%" >nul 2>&1

if %errorLevel% == 0 (
    echo [OK] FFmpeg adicionado ao PATH com sucesso!
    echo.
    echo IMPORTANTE:
    echo - Feche e reabra o Prompt de Comando para usar o ffmpeg
    echo - Ou reinicie o computador para garantir que funcione em todos os programas
    echo.
    echo Para testar, abra um novo Prompt de Comando e digite:
    echo   ffmpeg -version
) else (
    echo [ERRO] Falha ao adicionar ao PATH!
    echo Tente executar novamente como Administrador.
)

echo.
pause