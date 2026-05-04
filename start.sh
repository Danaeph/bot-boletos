#!/bin/bash

echo "Instalando Chromium..."
playwright install chromium

echo "Iniciando bot..."
python bot.py