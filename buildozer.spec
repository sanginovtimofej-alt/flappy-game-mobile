[app]
title = FlappyTabs
package.name = flappytabs
package.domain = org.game
source.dir = .
source.include_exts = py,png,jpg,json,ttf
version = 1.0

# Фиксируем чистый pygame
requirements = python3,pygame

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a

# КРИТИЧЕСКИЙ ФИКС: Откатываем NDK на r25c для совместимости с SDL2 Mixer
android.ndk = 25c
android.api = 33
android.minapi = 24

# Подключаем стабильную ветку сборщика
p4a.branch = master

android.allow_backup = True
