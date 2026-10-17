from datetime import datetime
import os
import sqlite3
from flask import Flask, redirect, render_template_string, request, url_for
import webview

app = Flask(__name__)
DB_PATH = "engineering_system.db"


# --- تنظیمات پایگاه داده ---
def init_db():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS calc_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            details TEXT,
            result TEXT
        )
    """)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS inspection_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            item_name TEXT,
            note TEXT,
            status TEXT,
            image_name TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

# --- قالب HTML و رابط کاربری مدرن با Bootstrap ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>عمران‌یاور | دستیار هوشمند مهندسین عمران</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <style>
        body { font-family: 'Vazirmatn', sans-serif; background-color: #f1f5f9; color: #1e293b; }
        .card { border: none; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border-radius: 16px; background-color: #ffffff; }
        .nav-tabs .nav-link.active { background-color: #312e81; color: white !important; font-weight: bold; border-radius: 10px 10px 0 0; border: none; }
        .nav-tabs .nav-link { color: #475569; font-weight: 600; cursor: pointer; border-radius: 10px 10px 0 0; margin-left: 4px; }
        .table th { background-color: #312e81 !important; color: white; text-align: center; font-size: 0.85rem; vertical-align: middle; }
        .table td { vertical-align: middle; text-align: center; }
        .btn-primary { background-color: #4f46e5; border-color: #4f46e5; border-radius: 10px; }
        .form-control, .form-select { border-radius: 10px; border: 1px solid #cbd5e1; padding: 10px 14px; }
    </style>
</head>
<body class="container py-4">
    <div class="card p-4 mb-4 shadow-sm text-center bg-indigo text-white" style="background: linear-gradient(135deg, #312e81 0%, #4f46e5 100%);">
        <h3 class="fw-bold mb-1 text-white">🏗️ عمران‌یاور | دستیار هوشمند مهندسین عمران</h3>
        <p class="mb-0 text-light small">مدیریت محاسبات، چک‌لیست‌های کارگاهی و آرشیو سوابق</p>
    </div>

    <ul class="nav nav-tabs mb-4 px-2" id="myTab" role="tablist">
        <li class="nav-item"><button class="nav-link active" id="calc-tab" data-bs-toggle="tab" data-bs-target="#calc-pane" type="button">🧮 ماشین‌حساب‌های عمرانی</button></li>
        <li class="nav-item"><button class="nav-link" id="inspect-tab" data-bs-toggle="tab" data-bs-target="#inspect-pane" type="button">📋 چک‌لیست و نظارت</button></li>
        <li class="nav-item"><button class="nav-link" id="archive-tab" data-bs-toggle="tab" data-bs-target="#archive-pane" type="button">📁 آرشیو سوابق و گزارش‌ها</button></li>
    </ul>

    <div class="tab-content" id="myTabContent">
        <!-- تب اول: ماشین‌حساب -->
        <div class="tab-pane fade show active" id="calc-pane" role="tabpanel">
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="card p-4">
                        <h5 class="fw-bold text-primary mb-3">⚖️ برآورد وزن میلگرد</h5>
                        <form method="POST" action="/calc_rebar">
                            <div class="mb-3">
                                <label class="form-label">قطر میلگرد (میلی‌متر):</label>
                                <input type="number" step="any" name="rebar_d" class="form-control" value="14" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">طول کل میلگرد (متر):</label>
                                <input type="number" step="any" name="rebar_l" class="form-control" value="12" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 shadow-sm">محاسبه و ذخیره در آرشیو 💾</button>
                        </form>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card p-4">
                        <h5 class="fw-bold text-primary mb-3">🧱 برآورد حجم بتن‌ریزی</h5>
                        <form method="POST" action="/calc_concrete">
                            <div class="row">
                                <div class="col-md-4 mb-3"><label class="form-label">طول (متر):</label><input type="number" step="any" name="conc_l" class="form-control" value="5" required></div>
                                <div class="col-md-4 mb-3"><label class="form-label">عرض (متر):</label><input type="number" step="any" name="conc_w" class="form-control" value="4" required></div>
                                <div class="col-md-4 mb-3"><label class="form-label">ارتفاع (متر):</label><input type="number" step="any" name="conc_h" class="form-control" value="0.3" required></div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 shadow-sm">محاسبه حجم (با احتساب ۵٪ پرتی) 💾</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- تب دوم: چک‌لیست نظارت -->
        <div class="tab-pane fade" id="inspect-pane" role="tabpanel">
            <div class="card p-4">
                <h5 class="fw-bold text-primary mb-3">📋 ثبت گزارش نظارت کارگاهی</h5>
                <form method="POST" action="/add_inspection">
                    <div class="mb-3">
                        <label class="form-label">تاریخ گزارش:</label>
                        <input type="text" name="insp_date" class="form-control" value="{{ today }}" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">انتخاب آیتم نظارتی:</label>
                        <select name="item_name" class="form-select">
                            <option>کنترل ابعاد فونداسیون و موقعیت ستون‌ها</option>
                            <option>بررسی کنترل میلگردهای طولی و خاموت‌ها</option>
                            <option>بررسی کیفیت بتن‌ریزی و تست‌های کارگاهی</option>
                            <option>کنترل شاقولی ستون‌ها و اتصالات جوشی/پیچی</option>
                            <option>بررسی اجرای صحیح وال‌پست‌ها و میان‌قابت‌ها</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">توضیحات و مشاهدات ناظر:</label>
                        <textarea name="note" class="form-control" rows="3" placeholder="ایرادات یا نکات اجرایی..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">نام فایل عکس پیوست (اختیاری):</label>
                        <input type="text" name="image_name" class="form-control" placeholder="مثلا photo1.jpg">
                    </div>
                    <div class="mb-3 form-check">
                        <input type="checkbox" name="status" value="تایید" class="form-check-input" id="chkStatus" checked>
                        <label class="form-check-label fw-bold text-success" for="chkStatus">آیتم تایید شد / بدون نقص</label>
                    </div>
                    <button type="submit" class="btn btn-success w-100 shadow-sm">ثبت گزارش نظارت در آرشیو ✅</button>
                </form>
            </div>
        </div>

        <!-- تب سوم: آرشیو سوابق -->
        <div class="tab-pane fade" id="archive-pane" role="tabpanel">
            <div class="card p-4 mb-4">
                <h5 class="fw-bold text-primary mb-3">📊 آرشیو محاسبات و گزارش‌های ثبت‌شده</h5>
                <div class="table-responsive">
                    <table class="table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>نوع رکورد</th>
                                <th>تاریخ</th>
                                <th>عنوان / جزئیات</th>
                                <th>نتیجه / وضعیت</th>
                                <th>پیوست / توضیحات</th>
                                <th>عملیات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in calc_rows %}
                            <tr>
                                <td><span class="badge bg-info text-dark">محاسبه</span></td>
                                <td>{{ row[1] }}</td>
                                <td>{{ row[2] }}</td>
                                <td class="fw-bold text-success">{{ row[4] }}</td>
                                <td>{{ row[3] }}</td>
                                <td>
                                    <form method="POST" action="/delete_calc/{{ row[0] }}" style="display:inline;">
                                        <button type="submit" class="btn btn-danger btn-sm">حذف 🗑️</button>
                                    </form>
                                </td>
                            </tr>
                            {% endfor %}
                            {% for row in insp_rows %}
                            <tr>
                                <td><span class="badge bg-warning text-dark">نظارت</span></td>
                                <td>{{ row[1] }}</td>
                                <td>{{ row[2] }}</td>
                                <td><span class="badge {{ 'bg-success' if row[4] == 'تایید' else 'bg-danger' }}">{{ row[4] }}</span></td>
                                <td>{{ row[3] }} {% if row[5] %}<br><small class="text-muted">📷 {{ row[5] }}</small>{% endif %}</td>
                                <td>
                                    <form method="POST" action="/delete_insp/{{ row[0] }}" style="display:inline;">
                                        <button type="submit" class="btn btn-danger btn-sm">حذف 🗑️</button>
                                    </form>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


# --- مسیرهای Flask ---
@app.route("/")
def index():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, date, title, details, result FROM calc_records ORDER BY id"
      " DESC"
  )
  calc_rows = cursor.fetchall()
  cursor.execute(
      "SELECT id, date, item_name, note, status, image_name FROM"
      " inspection_records ORDER BY id DESC"
  )
  insp_rows = cursor.fetchall()
  conn.close()

  today = datetime.now().strftime("%Y-%m-%d")
  return render_template_string(
      HTML_TEMPLATE,
      calc_rows=calc_rows,
      insp_rows=insp_rows,
      today=today,
  )


@app.route("/calc_rebar", methods=["POST"])
def calc_rebar():
  try:
    d = float(request.form.get("rebar_d"))
    l = float(request.form.get("rebar_l"))
    weight = (d**2 / 162.0) * l
    res_str = f"{weight:.2f} کیلوگرم"
    details = f"قطر {d}mm | طول {l}m"
    date_str = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO calc_records (date, title, details, result) VALUES (?, ?,"
        " ?, ?)",
        (date_str, "محاسبه وزن میلگرد", details, res_str),
    )
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"Error: {e}")
  return redirect(url_for("index"))


@app.route("/calc_concrete", methods=["POST"])
def calc_concrete():
  try:
    l = float(request.form.get("conc_l"))
    w = float(request.form.get("conc_w"))
    h = float(request.form.get("conc_h"))
    volume = l * w * h
    volume_waste = volume * 1.05
    res_str = f"خالص: {volume:.2f} m³ | با پرتی: {volume_waste:.2f} m³"
    details = f"ابعاد: {l}x{w}x{h} متر"
    date_str = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO calc_records (date, title, details, result) VALUES (?, ?,"
        " ?, ?)",
        (date_str, "محاسبه حجم بتن", details, res_str),
    )
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"Error: {e}")
  return redirect(url_for("index"))


@app.route("/add_inspection", methods=["POST"])
def add_inspection():
  try:
    date_str = request.form.get("insp_date")
    item_name = request.form.get("item_name")
    note = request.form.get("note", "بدون توضیح")
    image_name = request.form.get("image_name", "")
    status = "تایید" if request.form.get("status") else "نیاز به اصلاح"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inspection_records (date, item_name, note, status,"
        " image_path) VALUES (?, ?, ?, ?, ?)",
        (date_str, item_name, note, status, image_name),
    )
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"Error: {e}")
  return redirect(url_for("index"))


@app.route("/delete_calc/<int:rec_id>", methods=["POST"])
def delete_calc(rec_id):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM calc_records WHERE id = ?", (rec_id,))
  conn.commit()
  conn.close()
  return redirect(url_for("index"))


@app.route("/delete_insp/<int:rec_id>", methods=["POST"])
def delete_insp(rec_id):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM inspection_records WHERE id = ?", (rec_id,))
  conn.commit()
  conn.close()
  return redirect(url_for("index"))


# --- اجرای برنامه با PyWebView به صورت نرم‌افزار دسکتاپ ---
if __name__ == "__main__":
  # باز کردن برنامه درون یک پنجره‌ی اختصاصی نرم‌افزاری بدون نیاز به مرورگر
  webview.create_window(
      "عمران‌یاور | دستیار هوشمند مهندسین", app, width=1050, height=750
  )
  webview.start()