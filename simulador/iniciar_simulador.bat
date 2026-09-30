@echo off
chcp 65001 >nul
title FluxoWMS - simulador (feche esta janela para desligar)
cd /d "%~dp0"
echo.
echo   FluxoWMS - Ambiente de demonstracao
echo   Endereco: http://localhost:8080
echo   Para desligar o simulador, feche esta janela.
echo.
where python >nul 2>nul || (echo [ERRO] Python nao encontrado. Instale o Python e tente de novo. & pause & exit /b 1)
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8080"
python -m http.server 8080 --bind 127.0.0.1
pause
