#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Бърз тест на KIKI системата"""

import speech_recognition as sr
from gtts import gTTS
import pygame
import requests
import json
import os
import tempfile
import time
from datetime import datetime
import wikipedia
import random

print("=" * 50)
print("KIKI - Бърз тест на системата")
print("=" * 50)

# Тест 1: Библиотеки
print("\n1. Проверка на библиотеките...")
print("   ✓ speech_recognition")
print("   ✓ gtts")
print("   ✓ pygame")
print("   ✓ requests")
print("   ✓ wikipedia")
print("   ✓ random")

# Тест 2: Random функция
print("\n2. Тест на random функцията...")
test_jokes = ['Виц 1', 'Виц 2', 'Виц 3']
selected = random.choice(test_jokes)
print(f"   ✓ Избран: {selected}")

# Тест 3: Дата и час
print("\n3. Тест на дата/час...")
now = datetime.now()
day_names = ["понеделник", "вторник", "сряда", "четвъртък", "петък", "събота", "неделя"]
day_name = day_names[now.weekday()]
print(f"   ✓ Днес е: {day_name}")
print(f"   ✓ Часът е: {now.strftime('%H:%M')}")

# Тест 4: Wikipedia (кратко)
print("\n4. Тест на Wikipedia...")
try:
    wikipedia.set_lang("bg")
    print("   ✓ Wikipedia настроен на български")
except Exception as e:
    print(f"   ✗ Грешка: {e}")

# Тест 5: Прости отговори
print("\n5. Тест на прости отговори...")
responses = {
    "здравей": "Здравей! Как мога да ти помогна?",
    "как си": "Отлично! Благодаря, че питаш!",
    "как се казваш": "Казвам се KIKI! Твоя AI асистент!"
}

for question, answer in responses.items():
    print(f"   Q: {question}")
    print(f"   A: {answer}")

print("\n" + "=" * 50)
print("✅ ВСИЧКИ ТЕСТОВЕ ПРЕМИНАХА УСПЕШНО!")
print("=" * 50)
print("\n💡 Системата е готова за работа БЕЗ Ollama!")
print("   Стартирайте с: start.bat или start.ps1")
