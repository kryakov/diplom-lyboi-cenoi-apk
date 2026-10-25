[app]
title = Диплом любой ценой
package.name = diplom
package.domain = org.tpproject
source.dir = .
source.include_exts = py,png,json,txt,ogg,wav,mp3,ttf
source.exclude_dirs = tests,tools,docs,release,bin,.github
source.exclude_patterns = README.md,buildozer.spec
version = 1.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
android.presplash_color = #1C1C2E
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
