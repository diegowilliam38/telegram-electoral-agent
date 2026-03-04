@echo off
title Agente Eleitoral - Telegram Bot
echo Iniciando o Agente Virtual...
echo.
call .venv\Scripts\activate
python -m src.bot
pause
