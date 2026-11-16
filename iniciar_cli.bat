@echo off
chcp 65001 > nul
title Pix Reverso CLI

cd /d "%~dp0"
python cli.py
pause
