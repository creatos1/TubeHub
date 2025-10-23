
[app]
title = YouTube Hub
package.name = youtubehub
package.domain = org.youtubehub

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db

version = 1.0

requirements = python3,kivy,kivymd,pillow,requests,sqlite3,sqlalchemy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 30
android.minapi = 29
android.ndk = 25b
android.sdk = 30

android.accept_sdk_license = True

android.gradle_dependencies = 

android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
