#!/bin/bash

echo "Instalando navegador..."

python -m playwright install chromium

echo "Iniciando bot..."

python bot.py
