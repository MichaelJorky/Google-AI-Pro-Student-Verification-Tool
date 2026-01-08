@echo off
title Script Runner v2
cls

:menu
echo ==========================================
echo       PILIH MODE MENJALANKAN SCRIPT
echo ==========================================
echo 1. Mode Interaktif
echo 2. Dengan URL Langsung
echo 3. Dengan Proxy (Host:Port)
echo 4. Dengan Proxy Auth (User:Pass@Host:Port)
echo 5. Keluar
echo ==========================================
set /p choice="Masukkan pilihan (1-5): "

if "%choice%"=="1" goto mode1
if "%choice%"=="2" goto mode2
if "%choice%"=="3" goto mode3
if "%choice%"=="4" goto mode4
if "%choice%"=="5" exit
goto menu

:mode1
echo [INFO] Menjalankan Mode Interaktif...
python.exe script.py
pause
goto menu

:mode2
set /p url="Masukkan URL_VERIFIKASI: "
python.exe script.py "%url%"
pause
goto menu

:mode3
set /p proxy_host="Masukkan Host:Port: "
set /p url="Masukkan URL_VERIFIKASI: "
python.exe script.py --proxy "http://%proxy_host%" "%url%"
pause
goto menu

:mode4
set /p proxy_auth="Masukkan User:Pass@Host:Port: "
set /p url="Masukkan URL_VERIFIKASI: "
python.exe script.py --proxy "http://%proxy_auth%" "%url%"
pause
goto menu