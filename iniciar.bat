@echo off
chcp 65001 > nul
title Pix Reverso - O Banco do Desperdício Consciente

echo ======================================================================
echo           💸 INICIANDO O SISTEMA DO PIX REVERSO 💸
echo  "Você paga para receber uma notificação de que poderia ter economizado"
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/2] Verificando dependências...
python -m pip install flask --quiet

echo [2/2] Abrindo navegador e iniciando servidor Flask...
start "" http://127.0.0.1:5000

echo.
echo ======================================================================
echo  Servidor rodando em: http://127.0.0.1:5000
echo  Para fechar o sistema, basta fechar esta janela do terminal.
echo ======================================================================
echo.

python app.py
pause
