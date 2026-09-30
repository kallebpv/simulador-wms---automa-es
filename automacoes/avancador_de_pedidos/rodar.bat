@echo off
chcp 65001 >nul
title FluxoWMS - Avançador de pedidos
cd /d "%~dp0"

rem ---- Ritmo da demonstração (para gravar vídeo) ----
rem VELOCIDADE_DEMO: 1 = ritmo original do robô | 2 = duas vezes mais rápido | 0.5 = mais devagar
rem PAUSA_EXTRA_DEMO: segundos a mais antes de cada ação
set VELOCIDADE_DEMO=1
set PAUSA_EXTRA_DEMO=0.6

where python >nul 2>nul || (echo [ERRO] Python nao encontrado. & pause & exit /b 1)

rem Instala as bibliotecas na primeira vez
python -c "import selenium, pandas, openpyxl, psutil, pyperclip, win32api" 2>nul || python -m pip install -r ..\requirements.txt

rem Confere se o simulador está ligado
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080', timeout=3)" 2>nul
if errorlevel 1 (
  echo.
  echo [ATENCAO] O simulador FluxoWMS nao esta ligado.
  echo Abra primeiro: simulador\iniciar_simulador.bat  e depois rode este arquivo de novo.
  echo.
  pause
  exit /b 1
)

python interface.py
pause
