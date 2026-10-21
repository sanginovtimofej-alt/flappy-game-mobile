[app]
title=FlappyTabs
package.name=flappytabs
package.domain=org.game
source.dir=.
source.include_exts=py,png,jpg,json,ttf
version=1.0

# ФИКС: Фиксируем стабильную мобильную версию pygame
requirements=python3,pygame==2.5.2

orientation=portrait
fullscreen=1

# Сборка только под современную 64-битную архитектуру, чтобы не перегружать компилятор кодеками
android.archs=arm64-v8a

android.allow_backup=True

# Оптимизация компилятора: отключаем тяжелые звуковые плагины, которые вызывают ошибку
android.meta_data=pygame.mixers=none
