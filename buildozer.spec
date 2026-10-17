[app]
# نام اپلیکیشن شما
title = عمران یاور
package.name = omranyavar
package.domain = org.engineering

# فایل‌های سورس پروژه که باید بسته‌بندی شوند
source.include_exts = py,png,jpg,kv,atlas
source.dir = .

# نسخه اپلیکیشن
version = 1.0

# پکیج‌های پایتون مورد نیاز برای اندروید
requirements = python3,flask,jinja2,werkzeug,click,itsdangerous

# جهت‌گیری صفحه (عمودی یا افقی)
orientation = portrait

# دسترسی‌های مورد نیاز اندروید (چون سرور لوکال فلاسْک اجرا می‌شود، دسترسی به اینترنت داخلی لازم است)
android.permissions = INTERNET

# سطح پلتفرم اندروید
android.api = 33
android.minapi = 21