@echo off
chcp 65001 >nul
title Oracle DB Manager - Build Script

echo ============================================================
echo 🏗️  ORACLE DB MANAGER - BUILD SCRIPT
echo ============================================================
echo.

echo 🧹 Limpando builds anteriores...

REM
if exist "dist" (
    rmdir /s /q "dist"
    echo 🗑️  Removido: dist/
)

if exist "build" (
    rmdir /s /q "build"  
    echo 🗑️  Removido: build/
)

echo.
echo 🚀 Iniciando build...
echo ⏳ Isso pode demorar alguns minutos...
echo.

REM
echo 📋 Executando comando PyInstaller...
echo.

python -m PyInstaller --onefile --windowed --name=OracleDBManager --add-data="services;services" --add-data="screens;screens" --add-data="utils;utils" --add-data="instantclient;instantclient" --hidden-import=uuid --hidden-import=cryptography.hazmat.primitives.kdf.pbkdf2 --hidden-import=cryptography.x509 main.py

REM
if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ Build concluído com sucesso!
    
    REM
    if exist "dist\OracleDBManager.exe" (
        echo 📁 Executável criado: dist\OracleDBManager.exe
        
        echo.
    ) else (
        echo ⚠️  Executável não encontrado no local esperado
    )
) else (
    echo.
    echo ❌ Erro durante o build!
    echo 🔧 Possíveis soluções:
    echo • Verifique se o PyInstaller está instalado: pip install pyinstaller
    echo • Certifique-se de que todas as dependências estão instaladas  
    echo • Verifique se não há erros no código Python
)

echo.
echo ============================================================
pause