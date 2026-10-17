[app]
title = عمران یاور
package.name = omranyavar
package.domain = org.engineering

source.include_exts = py,png,jpg,kv,atlas
source.dir = .

version = 1.0

# پکیج‌های پایتون مورد نیاز
requirements = python3,flask,jinja2,werkzeug,click,itsdangerous

orientation = portrait
android.permissions = INTERNET

# تنظیم نسخه‌های پایدار و پذیرش خودکار لایسنس
android.api = 34
android.minapi = 21
android.sdk = 34
android.accept_sdk_license = True