# test_ui.py
"""
تست ویجت‌های UI
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# اضافه کردن مسیر پروژه
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.colors import APP_COLORS
from ui.widgets.tables import SearchableTable
from ui.widgets.forms import GarmentEntryForm


def test_tables():
    """تست جداول"""
    print("🧪 تست جداول...")

    root = tk.Tk()
    root.title("تست جداول")
    root.geometry("900x600")
    root.configure(bg=APP_COLORS['bg'])

    # ایجاد فریم اصلی
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # ایجاد جدول
    columns = ('row_num', 'product_code', 'product_name', 'color', 'quantity')
    column_config = {
        'row_num': ('ردیف', 60, 'center'),
        'product_code': ('کد محصول', 120, 'center'),
        'product_name': ('نام محصول', 200, 'center'),
        'color': ('رنگ', 100, 'center'),
        'quantity': ('تعداد', 80, 'center')
    }

    table = SearchableTable(main_frame, columns, column_config, height=10)
    table.pack(fill='both', expand=True)

    # داده‌های نمونه
    sample_data = [
        (1, 'PRD-001', 'پیراهن مردانه', 'آبی', 50),
        (2, 'PRD-002', 'شلوار زنانه', 'سیاه', 30),
        (3, 'PRD-003', 'ژاکت بچگانه', 'قرمز', 20),
        (4, 'PRD-004', 'کفش ورزشی', 'سفید', 15),
        (5, 'PRD-005', 'کلاه زمستانی', 'خاکستری', 25),
        (6, 'PRD-006', 'دستکش چرمی', 'قهوه‌ای', 40),
        (7, 'PRD-007', 'روسری ابریشمی', 'صورتی', 35),
        (8, 'PRD-008', 'کمربند چرم', 'مشکی', 60),
        (9, 'PRD-009', 'جوراب نخی', 'سفید', 100),
        (10, 'PRD-010', 'مانتو زنانه', 'بنفش', 18)
    ]

    # بارگذاری داده‌ها
    table.load_data(sample_data)

    # اطلاعات
    info_label = ttk.Label(main_frame,
                           text="برای تست: در فیلد جستجو تایپ کنید - روی سطر دابل کلیک کنید")
    info_label.pack(pady=10)

    # رویداد دابل کلیک
    def on_double_click(event):
        selected = table.get_selected_row()
        if selected:
            print(f"✅ ردیف انتخاب شده: {selected}")
            info_label.config(text=f"انتخاب: کد {selected[1]} - {selected[2]}")

    table.tree.bind('<<TreeviewDoubleClick>>', on_double_click)

    root.mainloop()


def test_forms():
    """تست فرم‌ها"""
    print("📝 تست فرم‌ها...")

    root = tk.Tk()
    root.title("تست فرم‌ها")
    root.geometry("700x800")
    root.configure(bg=APP_COLORS['bg'])

    # ایجاد فریم اصلی با اسکرول
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # کانوس برای اسکرول
    canvas = tk.Canvas(main_frame, bg=APP_COLORS['content_bg'], highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, bg=APP_COLORS['content_bg'])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # ایجاد فرم
    form = GarmentEntryForm(scrollable_frame)

    # دکمه‌های فرم
    btn_frame = ttk.Frame(scrollable_frame)
    btn_frame.grid(row=10, column=0, columnspan=2, pady=20)

    def on_submit():
        data = form.get_data()
        errors = form.validate()

        if errors:
            print("❌ خطاهای فرم:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ فرم معتبر است!")
            print("📊 داده‌های فرم:")
            for key, value in data.items():
                print(f"   {key}: {value}")

    submit_btn = ttk.Button(btn_frame, text="تست اعتبارسنجی",
                            command=on_submit)
    submit_btn.pack(side='left', padx=10)

    clear_btn = ttk.Button(btn_frame, text="پاک کردن فرم",
                           command=form.clear)
    clear_btn.pack(side='left', padx=10)

    # تنظیم layout
    scrollable_frame.grid_columnconfigure(1, weight=1)

    root.mainloop()


def main():
    """تابع اصلی تست"""
    print("🔧 تست ویجت‌های UI")
    print("=" * 50)

    choice = input("کدام تست را می‌خواهید؟\n1. جداول\n2. فرم‌ها\n3. هر دو\nانتخاب (1-3): ")

    if choice == '1':
        test_tables()
    elif choice == '2':
        test_forms()
    elif choice == '3':
        print("⚠️ لطفاً پنجره اول را ببندید تا تست دوم شروع شود")
        test_tables()
        test_forms()
    else:
        print("❌ انتخاب نامعتبر")


if __name__ == "__main__":
    main()