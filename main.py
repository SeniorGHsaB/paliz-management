import tkinter as tk
from tkinter import ttk, font, messagebox, simpledialog
import ctypes
from datetime import datetime, date
import sqlite3
import json
import os
from tkcalendar import DateEntry  # نیاز به نصب: pip install tkcalendar
import csv

# تنظیم DPI برای ویندوز
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class GarmentPackagingManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("مدیریت کارگاه بسته‌بندی لباس")

        # تنظیم فول اسکرین
        self.is_fullscreen = True
        self.root.attributes('-fullscreen', True)

        # رنگ‌های برنامه
        self.colors = {
            'bg': '#f5f5f5',
            'sidebar': '#2c3e50',
            'sidebar_hover': '#34495e',
            'sidebar_active': '#1abc9c',
            'content_bg': '#ffffff',
            'header_bg': '#ecf0f1',
            'text_light': '#ffffff',
            'text_dark': '#2c3e50',
            'text_gray': '#7f8c8d',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#3498db',
            'border': '#bdc3c7'
        }

        # رنگ‌های پارچه
        self.fabric_colors = [
            "سیاه", "سفید", "قرمز", "آبی", "سبز",
            "زرد", "سرمه‌ای", "قهوه‌ای", "بنفش", "نارنجی",
            "صورتی", "طلایی", "نقره‌ای", "خاکستری", "بژ"
        ]

        # انواع پارچه
        self.fabric_types = [
            "کتان", "پنبه", "ابریشم", "نخ", "پلی‌استر",
            "ویسکوز", "لنین", "جین", "حریر", "کرپ"
        ]

        # سایزها
        self.sizes = ["تک سایز", "سایز 1", "سایز 2", "S", "M", "L", "XL", "XXL"]

        # کیفیت محصولات
        self.qualities = ["درجه 1", "درجه 2", "معمولی"]

        self.setup_fonts()
        self.setup_database()
        self.setup_ui()
        self.bind_events()

    def setup_fonts(self):
        """تنظیم فونت‌ها"""
        self.fonts = {
            'title': font.Font(family="Segoe UI", size=18, weight="bold"),
            'subtitle': font.Font(family="Segoe UI", size=14, weight="bold"),
            'normal': font.Font(family="Segoe UI", size=11),
            'small': font.Font(family="Segoe UI", size=9),
            'large': font.Font(family="Segoe UI", size=16)
        }

    def setup_database(self):
        """تنظیم پایگاه داده"""
        self.conn = sqlite3.connect('garment_factory.db')
        self.cursor = self.conn.cursor()

        # ایجاد جدول ورودی پوشاک
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS garment_entries
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                product_name
                                TEXT
                                NOT
                                NULL,
                                product_code
                                TEXT
                                UNIQUE
                                NOT
                                NULL,
                                size
                                TEXT
                                NOT
                                NULL,
                                color
                                TEXT
                                NOT
                                NULL,
                                custom_color
                                TEXT,
                                fabric_type
                                TEXT
                                NOT
                                NULL,
                                cutting_code
                                TEXT
                                NOT
                                NULL,
                                entry_date
                                DATE
                                NOT
                                NULL,
                                tailor_name
                                TEXT
                                NOT
                                NULL,
                                quantity
                                INTEGER
                                DEFAULT
                                1,
                                notes
                                TEXT,
                                created_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP
                            )
                            ''')

        # ایجاد جدول خروجی پوشاک
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS garment_outputs
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                garment_id
                                INTEGER,
                                product_code
                                TEXT
                                NOT
                                NULL,
                                output_date
                                DATE
                                NOT
                                NULL,
                                quality
                                TEXT
                                NOT
                                NULL,
                                destination
                                TEXT,
                                quantity
                                INTEGER
                                DEFAULT
                                1,
                                package_code
                                TEXT,
                                notes
                                TEXT,
                                created_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP,
                                FOREIGN
                                KEY
                            (
                                garment_id
                            ) REFERENCES garment_entries
                            (
                                id
                            )
                                )
                            ''')

        # ایجاد جدول کارمندان
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS employees
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                first_name
                                TEXT
                                NOT
                                NULL,
                                last_name
                                TEXT
                                NOT
                                NULL,
                                national_id
                                TEXT
                                UNIQUE,
                                birth_date
                                DATE,
                                address
                                TEXT,
                                phone
                                TEXT
                                NOT
                                NULL,
                                position
                                TEXT,
                                hire_date
                                DATE,
                                salary
                                REAL,
                                status
                                TEXT
                                DEFAULT
                                'فعال',
                                notes
                                TEXT,
                                created_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP
                            )
                            ''')

        self.conn.commit()

    def setup_ui(self):
        """ایجاد رابط کاربری"""
        # پنل سمت چپ
        self.create_sidebar()

        # ناحیه محتوا
        self.create_content_area()

        # نمایش صفحه اصلی اولیه
        self.show_dashboard()

    def create_sidebar(self):
        """ایجاد پنل سمت چپ"""
        self.sidebar = tk.Frame(self.root, bg=self.colors['sidebar'], width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # عنوان پنل
        title_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_active'], height=70)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="👕 کارگاه بسته‌بندی",
                 bg=self.colors['sidebar_active'],
                 fg=self.colors['text_light'],
                 font=self.fonts['title']).pack(expand=True, pady=10)

        # آیتم‌های منو
        menu_items = [
            ("📊", "داشبورد", "dashboard"),
            ("📥", "ورودی پوشاک", "garment_entry"),
            ("📤", "خروجی کارگاه", "garment_output"),
            ("👥", "مدیریت کارمندان", "employee_management"),
            ("🔍", "جستجوی پیشرفته", "advanced_search"),
            ("📋", "گزارشات", "reports"),
            ("⚙️", "تنظیمات", "settings"),
            ("🚪", "خروج", "exit")
        ]

        self.menu_buttons = []

        for icon, text, page_id in menu_items:
            btn = self.create_menu_button(self.sidebar, icon, text, page_id)
            btn.pack(fill='x', pady=1)
            self.menu_buttons.append(btn)

        # آمار سریع
        stats_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'], pady=20)
        stats_frame.pack(side='bottom', fill='x', padx=10)

        self.stats_labels = {}
        stats_data = [
            ("📦", "ورودی امروز", "0"),
            ("📤", "خروجی امروز", "0"),
            ("👥", "کارمندان فعال", "0"),
            ("👕", "موجودی انبار", "0")
        ]

        for icon, title, value in stats_data:
            stat_widget = self.create_stat_widget(stats_frame, icon, title, value)
            stat_widget.pack(fill='x', pady=3)
            self.stats_labels[title] = stat_widget.nametowidget(stat_widget.winfo_children()[-1].winfo_children()[-1])

    def create_menu_button(self, parent, icon, text, page_id):
        """ایجاد دکمه منو"""
        btn_frame = tk.Frame(parent, bg=self.colors['sidebar'], cursor='hand2', height=50)
        btn_frame.pack_propagate(False)

        # آیکون
        icon_label = tk.Label(btn_frame,
                              text=icon,
                              font=self.fonts['large'],
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_light'],
                              padx=15)
        icon_label.pack(side='left')

        # متن
        text_label = tk.Label(btn_frame,
                              text=text,
                              font=self.fonts['normal'],
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_light'])
        text_label.pack(side='left', fill='x', expand=True, anchor='w')

        # نشانگر فعال
        indicator = tk.Frame(btn_frame, bg=self.colors['sidebar'], width=4)
        indicator.pack(side='right', fill='y')

        # ذخیره اطلاعات
        btn_frame.icon_label = icon_label
        btn_frame.text_label = text_label
        btn_frame.indicator = indicator
        btn_frame.page_id = page_id
        btn_frame.is_active = False

        # رویدادهای ماوس
        def on_enter(e):
            if not btn_frame.is_active:
                btn_frame.config(bg=self.colors['sidebar_hover'])
                icon_label.config(bg=self.colors['sidebar_hover'])
                text_label.config(bg=self.colors['sidebar_hover'])
                indicator.config(bg=self.colors['sidebar_hover'])

        def on_leave(e):
            if not btn_frame.is_active:
                btn_frame.config(bg=self.colors['sidebar'])
                icon_label.config(bg=self.colors['sidebar'])
                text_label.config(bg=self.colors['sidebar'])
                indicator.config(bg=self.colors['sidebar'])

        def on_click(e):
            self.set_active_menu(btn_frame)
            self.show_page(page_id)

        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        btn_frame.bind("<Button-1>", on_click)

        icon_label.bind("<Enter>", on_enter)
        icon_label.bind("<Leave>", on_leave)
        icon_label.bind("<Button-1>", on_click)

        text_label.bind("<Enter>", on_enter)
        text_label.bind("<Leave>", on_leave)
        text_label.bind("<Button-1>", on_click)

        return btn_frame

    def set_active_menu(self, active_button):
        """تنظیم منوی فعال"""
        for btn in self.menu_buttons:
            if btn == active_button:
                btn.config(bg=self.colors['sidebar_active'])
                btn.icon_label.config(bg=self.colors['sidebar_active'])
                btn.text_label.config(bg=self.colors['sidebar_active'])
                btn.indicator.config(bg=self.colors['sidebar_active'])
                btn.is_active = True
            else:
                btn.config(bg=self.colors['sidebar'])
                btn.icon_label.config(bg=self.colors['sidebar'])
                btn.text_label.config(bg=self.colors['sidebar'])
                btn.indicator.config(bg=self.colors['sidebar'])
                btn.is_active = False

    def create_stat_widget(self, parent, icon, title, value):
        """ایجاد ویجت آمار"""
        frame = tk.Frame(parent, bg=self.colors['sidebar'])

        # آیکون
        tk.Label(frame, text=icon, font=self.fonts['large'],
                 bg=self.colors['sidebar'], fg=self.colors['sidebar_active']).pack(side='left', padx=5)

        # متن و مقدار
        text_frame = tk.Frame(frame, bg=self.colors['sidebar'])
        text_frame.pack(side='left', fill='x', expand=True)

        tk.Label(text_frame, text=title, font=self.fonts['small'],
                 bg=self.colors['sidebar'], fg=self.colors['text_light']).pack(anchor='w')
        value_label = tk.Label(text_frame, text=value, font=self.fonts['subtitle'],
                               bg=self.colors['sidebar'], fg=self.colors['sidebar_active'])
        value_label.pack(anchor='w')

        return frame

    def create_content_area(self):
        """ایجاد ناحیه محتوا"""
        # هدر
        self.header = tk.Frame(self.root, bg=self.colors['header_bg'], height=70)
        self.header.pack(fill='x')
        self.header.pack_propagate(False)

        # عنوان صفحه
        self.page_title = tk.Label(self.header,
                                   text="داشبورد مدیریت",
                                   bg=self.colors['header_bg'],
                                   fg=self.colors['text_dark'],
                                   font=self.fonts['title'])
        self.page_title.pack(side='left', padx=30)

        # تاریخ و زمان
        time_frame = tk.Frame(self.header, bg=self.colors['header_bg'])
        time_frame.pack(side='right', padx=20)

        self.date_label = tk.Label(time_frame,
                                   text=datetime.now().strftime("%Y/%m/%d"),
                                   bg=self.colors['header_bg'],
                                   fg=self.colors['text_gray'],
                                   font=self.fonts['normal'])
        self.date_label.pack()

        self.time_label = tk.Label(time_frame,
                                   text=datetime.now().strftime("%H:%M:%S"),
                                   bg=self.colors['header_bg'],
                                   fg=self.colors['text_dark'],
                                   font=self.fonts['subtitle'])
        self.time_label.pack()

        # دکمه کنترل پنجره
        controls_frame = tk.Frame(self.header, bg=self.colors['header_bg'])
        controls_frame.pack(side='right', padx=10)

        # دکمه کمینه
        min_btn = tk.Label(controls_frame, text="─",
                           bg=self.colors['header_bg'],
                           fg=self.colors['text_dark'],
                           font=("Arial", 16),
                           padx=12,
                           cursor='hand2')
        min_btn.pack(side='left')
        min_btn.bind("<Button-1>", lambda e: self.root.state('iconic'))
        min_btn.bind("<Enter>", lambda e: min_btn.config(bg=self.colors['border']))
        min_btn.bind("<Leave>", lambda e: min_btn.config(bg=self.colors['header_bg']))

        # دکمه فول اسکرین
        self.fullscreen_btn = tk.Label(controls_frame, text="⛶",
                                       bg=self.colors['header_bg'],
                                       fg=self.colors['text_dark'],
                                       font=("Arial", 14),
                                       padx=12,
                                       cursor='hand2')
        self.fullscreen_btn.pack(side='left')
        self.fullscreen_btn.bind("<Button-1>", lambda e: self.toggle_fullscreen())
        self.fullscreen_btn.bind("<Enter>", lambda e: self.fullscreen_btn.config(bg=self.colors['border']))
        self.fullscreen_btn.bind("<Leave>", lambda e: self.fullscreen_btn.config(bg=self.colors['header_bg']))

        # دکمه بستن
        close_btn = tk.Label(controls_frame, text="✕",
                             bg=self.colors['header_bg'],
                             fg=self.colors['text_dark'],
                             font=("Arial", 14),
                             padx=12,
                             cursor='hand2')
        close_btn.pack(side='left')
        close_btn.bind("<Button-1>", lambda e: self.exit_app())
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=self.colors['danger'], fg='white'))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.colors['header_bg'], fg=self.colors['text_dark']))

        # محتوای اصلی
        self.content_frame = tk.Frame(self.root, bg=self.colors['content_bg'])
        self.content_frame.pack(fill='both', expand=True)

    def clear_content(self):
        """پاک کردن محتوا"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_page(self, page_id):
        """نمایش صفحه مورد نظر"""
        self.clear_content()

        if page_id == "dashboard":
            self.show_dashboard()
            self.page_title.config(text="داشبورد مدیریت")
        elif page_id == "garment_entry":
            self.show_garment_entry()
            self.page_title.config(text="ورودی پوشاک")
        elif page_id == "garment_output":
            self.show_garment_output()
            self.page_title.config(text="خروجی کارگاه")
        elif page_id == "employee_management":
            self.show_employee_management()
            self.page_title.config(text="مدیریت کارمندان")
        elif page_id == "advanced_search":
            self.show_advanced_search()
            self.page_title.config(text="جستجوی پیشرفته")
        elif page_id == "reports":
            self.show_reports()
            self.page_title.config(text="گزارشات")
        elif page_id == "settings":
            self.show_settings()
            self.page_title.config(text="تنظیمات")
        elif page_id == "exit":
            self.exit_app()

        # به‌روزرسانی آمار
        self.update_stats()

    def show_dashboard(self):
        """نمایش داشبورد"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # کارت‌های آمار
        stats_frame = tk.Frame(container, bg=self.colors['content_bg'])
        stats_frame.pack(fill='x', pady=(0, 30))

        stats = [
            ("📦", "کل ورودی‌ها", self.get_total_entries(), self.colors['info']),
            ("📤", "کل خروجی‌ها", self.get_total_outputs(), self.colors['success']),
            ("👥", "کارمندان", self.get_total_employees(), self.colors['warning']),
            ("📊", "موجودی انبار", self.get_inventory_count(), self.colors['danger'])
        ]

        for i, (icon, title, value, color) in enumerate(stats):
            card = self.create_dashboard_card(stats_frame, icon, title, value, color)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            stats_frame.columnconfigure(i, weight=1)

        # فعالیت‌های اخیر
        tk.Label(container, text="آخرین ورودی‌ها",
                 font=self.fonts['subtitle'],
                 bg=self.colors['content_bg']).pack(anchor='w', pady=(0, 10))

        recent_frame = tk.Frame(container, bg=self.colors['content_bg'])
        recent_frame.pack(fill='both', expand=True)

        # جدول آخرین ورودی‌ها
        self.create_recent_table(recent_frame)

    def show_garment_entry(self):
        """نمایش فرم ورودی پوشاک"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # فرم ورودی
        form_frame = tk.Frame(container, bg=self.colors['content_bg'])
        form_frame.pack(fill='both', expand=True)

        # اسکرول‌بار
        canvas = tk.Canvas(form_frame, bg=self.colors['content_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['content_bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # فیلدهای فرم
        fields_frame = tk.Frame(scrollable_frame, bg=self.colors['content_bg'], padx=20, pady=20)
        fields_frame.pack(fill='both', expand=True)

        row = 0

        # نام محصول
        tk.Label(fields_frame, text="نام محصول:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.product_name_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.product_name_entry.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        # کد محصول
        tk.Label(fields_frame, text="کد محصول:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.product_code_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.product_code_entry.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        # سایز
        tk.Label(fields_frame, text="سایز:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.size_var = tk.StringVar()
        size_frame = tk.Frame(fields_frame, bg=self.colors['content_bg'])
        size_frame.grid(row=row, column=1, sticky='w', pady=15, padx=5)

        tk.Radiobutton(size_frame, text="تک سایز", variable=self.size_var,
                       value="تک سایز", bg=self.colors['content_bg'],
                       font=self.fonts['normal']).pack(side='left', padx=10)
        tk.Radiobutton(size_frame, text="سایز 1 و 2", variable=self.size_var,
                       value="سایز 1 و 2", bg=self.colors['content_bg'],
                       font=self.fonts['normal']).pack(side='left', padx=10)

        # گزینه‌های دیگر سایز
        self.size_combo = ttk.Combobox(size_frame, values=self.sizes,
                                       font=self.fonts['normal'], width=10, state='readonly')
        self.size_combo.pack(side='left', padx=10)
        self.size_var.set("تک سایز")
        row += 1

        # رنگ
        tk.Label(fields_frame, text="رنگ:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)

        color_frame = tk.Frame(fields_frame, bg=self.colors['content_bg'])
        color_frame.grid(row=row, column=1, sticky='w', pady=15, padx=5)

        self.color_var = tk.StringVar()
        self.color_combo = ttk.Combobox(color_frame, values=self.fabric_colors,
                                        textvariable=self.color_var,
                                        font=self.fonts['normal'], width=15, state='readonly')
        self.color_combo.pack(side='left', padx=5)

        tk.Label(color_frame, text="یا رنگ سفارشی:",
                 font=self.fonts['small'],
                 bg=self.colors['content_bg']).pack(side='left', padx=10)

        self.custom_color_entry = tk.Entry(color_frame, font=self.fonts['normal'], width=15)
        self.custom_color_entry.pack(side='left', padx=5)
        row += 1

        # نوع پارچه
        tk.Label(fields_frame, text="نوع پارچه:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.fabric_type_combo = ttk.Combobox(fields_frame, values=self.fabric_types,
                                              font=self.fonts['normal'], width=30, state='readonly')
        self.fabric_type_combo.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        # کد برش
        tk.Label(fields_frame, text="کد برش:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.cutting_code_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.cutting_code_entry.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        # تاریخ ورود
        tk.Label(fields_frame, text="تاریخ ورود:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.entry_date_entry = DateEntry(fields_frame, font=self.fonts['normal'],
                                          width=30, background='darkblue',
                                          foreground='white', borderwidth=2,
                                          date_pattern='yyyy-mm-dd')
        self.entry_date_entry.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        # نام دوزنده
        tk.Label(fields_frame, text="نام دوزنده:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.tailor_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.tailor_entry.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        # تعداد
        tk.Label(fields_frame, text="تعداد:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=15, padx=5)
        self.quantity_entry = tk.Spinbox(fields_frame, from_=1, to=1000,
                                         font=self.fonts['normal'], width=28)
        self.quantity_entry.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        # توضیحات
        tk.Label(fields_frame, text="توضیحات:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='nw', pady=15, padx=5)
        self.notes_text = tk.Text(fields_frame, font=self.fonts['normal'],
                                  width=30, height=4)
        self.notes_text.grid(row=row, column=1, sticky='w', pady=15, padx=5)
        row += 1

        fields_frame.columnconfigure(1, weight=1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # دکمه‌های فرم
        buttons_frame = tk.Frame(container, bg=self.colors['content_bg'])
        buttons_frame.pack(fill='x', pady=20)

        tk.Button(buttons_frame, text="📥 ثبت ورودی",
                  bg=self.colors['success'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=30,
                  pady=12,
                  command=self.save_garment_entry).pack(side='right', padx=10)

        tk.Button(buttons_frame, text="🧹 پاک کردن فرم",
                  bg=self.colors['warning'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=30,
                  pady=12,
                  command=self.clear_garment_form).pack(side='right', padx=10)

    def show_garment_output(self):
        """نمایش فرم خروجی کارگاه"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # دو تب برای خروجی و نمایش
        notebook = ttk.Notebook(container)
        notebook.pack(fill='both', expand=True)

        # تب ثبت خروجی
        output_tab = tk.Frame(notebook, bg=self.colors['content_bg'])
        notebook.add(output_tab, text='📤 ثبت خروجی')

        # تب نمایش خروجی‌ها
        view_tab = tk.Frame(notebook, bg=self.colors['content_bg'])
        notebook.add(view_tab, text='📋 لیست خروجی‌ها')

        # محتوای تب ثبت خروجی
        output_frame = tk.Frame(output_tab, bg=self.colors['content_bg'], padx=20, pady=20)
        output_frame.pack(fill='both', expand=True)

        # جستجوی محصول برای خروجی
        search_frame = tk.Frame(output_frame, bg=self.colors['content_bg'])
        search_frame.pack(fill='x', pady=(0, 20))

        tk.Label(search_frame, text="جستجوی محصول:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).pack(side='left', padx=5)

        self.output_search_entry = tk.Entry(search_frame, font=self.fonts['normal'], width=30)
        self.output_search_entry.pack(side='left', padx=5)

        tk.Button(search_frame, text="🔍 جستجو",
                  bg=self.colors['info'],
                  fg='white',
                  font=self.fonts['small'],
                  command=self.search_product_for_output).pack(side='left', padx=5)

        # نتایج جستجو
        self.output_results_frame = tk.Frame(output_frame, bg=self.colors['content_bg'])
        self.output_results_frame.pack(fill='x', pady=(0, 20))

        # فرم خروجی
        form_frame = tk.Frame(output_frame, bg=self.colors['content_bg'])
        form_frame.pack(fill='x')

        row = 0

        # کد محصول
        tk.Label(form_frame, text="کد محصول:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_product_code = tk.StringVar()
        tk.Label(form_frame, textvariable=self.output_product_code,
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg'],
                 fg=self.colors['text_gray']).grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تاریخ خروج
        tk.Label(form_frame, text="تاریخ خروج:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_date_entry = DateEntry(form_frame, font=self.fonts['normal'],
                                           width=30, background='darkblue',
                                           foreground='white', borderwidth=2,
                                           date_pattern='yyyy-mm-dd')
        self.output_date_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # کیفیت
        tk.Label(form_frame, text="کیفیت:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(form_frame, textvariable=self.quality_var,
                                     values=self.qualities,
                                     font=self.fonts['normal'], width=28, state='readonly')
        quality_combo.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # مقصد
        tk.Label(form_frame, text="مقصد:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.destination_entry = tk.Entry(form_frame, font=self.fonts['normal'], width=30)
        self.destination_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تعداد
        tk.Label(form_frame, text="تعداد:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_quantity = tk.Spinbox(form_frame, from_=1, to=1000,
                                          font=self.fonts['normal'], width=28)
        self.output_quantity.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # کد بسته‌بندی
        tk.Label(form_frame, text="کد بسته‌بندی:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.package_code_entry = tk.Entry(form_frame, font=self.fonts['normal'], width=30)
        self.package_code_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # توضیحات
        tk.Label(form_frame, text="توضیحات:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_notes_entry = tk.Entry(form_frame, font=self.fonts['normal'], width=30)
        self.output_notes_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)

        form_frame.columnconfigure(1, weight=1)

        # دکمه ثبت خروجی
        tk.Button(output_frame, text="✅ ثبت خروجی",
                  bg=self.colors['success'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=30,
                  pady=10,
                  command=self.save_garment_output).pack(pady=20)

        # محتوای تب نمایش خروجی‌ها
        self.create_outputs_table(view_tab)

    def show_employee_management(self):
        """نمایش مدیریت کارمندان"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # دو تب برای مدیریت کارمندان
        notebook = ttk.Notebook(container)
        notebook.pack(fill='both', expand=True)

        # تب ثبت کارمند جدید
        add_tab = tk.Frame(notebook, bg=self.colors['content_bg'])
        notebook.add(add_tab, text='👤 افزودن کارمند')

        # تب لیست کارمندان
        list_tab = tk.Frame(notebook, bg=self.colors['content_bg'])
        notebook.add(list_tab, text='📋 لیست کارمندان')

        # محتوای تب ثبت کارمند
        self.create_employee_form(add_tab)

        # محتوای تب لیست کارمندان
        self.create_employees_table(list_tab)

    def show_advanced_search(self):
        """نمایش جستجوی پیشرفته"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # تب‌های جستجو
        notebook = ttk.Notebook(container)
        notebook.pack(fill='both', expand=True)

        # تب جستجوی ورودی‌ها
        entry_search_tab = tk.Frame(notebook, bg=self.colors['content_bg'])
        notebook.add(entry_search_tab, text='🔍 جستجوی ورودی‌ها')

        # تب جستجوی خروجی‌ها
        output_search_tab = tk.Frame(notebook, bg=self.colors['content_bg'])
        notebook.add(output_search_tab, text='🔍 جستجوی خروجی‌ها')

        # تب جستجوی ترکیبی
        combined_search_tab = tk.Frame(notebook, bg=self.colors['content_bg'])
        notebook.add(combined_search_tab, text='🔍 جستجوی ترکیبی')

        # ایجاد فرم‌های جستجو
        self.create_entry_search_form(entry_search_tab)
        self.create_output_search_form(output_search_tab)
        self.create_combined_search_form(combined_search_tab)

    def show_reports(self):
        """نمایش گزارشات"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # انواع گزارشات
        reports_frame = tk.Frame(container, bg=self.colors['content_bg'])
        reports_frame.pack(fill='both', expand=True)

        reports = [
            ("📊", "گزارش روزانه", "گزارش ورودی و خروجی امروز", self.generate_daily_report),
            ("📈", "گزارش ماهانه", "گزارش عملکرد ماه جاری", self.generate_monthly_report),
            ("👕", "گزارش موجودی", "وضعیت انبار بر اساس رنگ و سایز", self.generate_inventory_report),
            ("👥", "گزارش کارمندان", "لیست کارمندان و عملکرد", self.generate_employee_report),
            ("📦", "گزارش کیفیت", "توزیع کیفیت محصولات خروجی", self.generate_quality_report),
            ("💾", "خروجی اکسل", "ذخیره همه داده‌ها در فایل اکسل", self.export_to_excel)
        ]

        for i, (icon, title, desc, command) in enumerate(reports):
            row = i // 3
            col = i % 3

            card = self.create_report_card(reports_frame, icon, title, desc, command)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            reports_frame.columnconfigure(col, weight=1)
            reports_frame.rowconfigure(row, weight=1)

    def show_settings(self):
        """نمایش تنظیمات"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        settings_frame = tk.Frame(container, bg=self.colors['content_bg'])
        settings_frame.pack(fill='both', expand=True)

        settings = [
            ("💾", "پشتیبان‌گیری", "تهیه نسخه پشتیبان از داده‌ها", self.backup_data),
            ("🔄", "بازیابی", "بازیابی داده‌ها از نسخه پشتیبان", self.restore_data),
            ("🧹", "پاکسازی", "پاکسازی داده‌های قدیمی", self.clean_old_data),
            ("⚙️", "تنظیمات سیستم", "تنظیمات پیشرفته سیستم", self.system_settings)
        ]

        for i, (icon, title, desc, command) in enumerate(settings):
            row = i // 2
            col = i % 2

            card = self.create_setting_card(settings_frame, icon, title, desc, command)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            settings_frame.columnconfigure(col, weight=1)
            settings_frame.rowconfigure(row, weight=1)

    def create_dashboard_card(self, parent, icon, title, value, color):
        """ایجاد کارت داشبورد"""
        card = tk.Frame(parent, bg='white',
                        highlightbackground=self.colors['border'],
                        highlightthickness=1,
                        cursor='hand2')

        content = tk.Frame(card, bg='white', padx=20, pady=20)
        content.pack(fill='both', expand=True)

        # آیکون
        tk.Label(content, text=icon,
                 font=self.fonts['large'],
                 bg='white').pack(anchor='w', pady=(0, 10))

        # عنوان
        tk.Label(content, text=title,
                 font=self.fonts['normal'],
                 bg='white',
                 fg=self.colors['text_gray']).pack(anchor='w', pady=(0, 5))

        # مقدار
        tk.Label(content, text=str(value),
                 font=self.fonts['title'],
                 bg='white',
                 fg=color).pack(anchor='w')

        return card

    def create_recent_table(self, parent):
        """ایجاد جدول آخرین ورودی‌ها"""
        # ایجاد Treeview
        columns = ('id', 'product_code', 'product_name', 'color', 'size', 'entry_date', 'tailor')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)

        # تعریف ستون‌ها
        tree.heading('id', text='شناسه')
        tree.heading('product_code', text='کد محصول')
        tree.heading('product_name', text='نام محصول')
        tree.heading('color', text='رنگ')
        tree.heading('size', text='سایز')
        tree.heading('entry_date', text='تاریخ ورود')
        tree.heading('tailor', text='دوزنده')

        tree.column('id', width=50)
        tree.column('product_code', width=100)
        tree.column('product_name', width=150)
        tree.column('color', width=80)
        tree.column('size', width=80)
        tree.column('entry_date', width=100)
        tree.column('tailor', width=120)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # دریافت داده‌های اخیر از دیتابیس
        try:
            self.cursor.execute('''
                                SELECT id, product_code, product_name, color, size, entry_date, tailor_name
                                FROM garment_entries
                                ORDER BY entry_date DESC
                                    LIMIT 10
                                ''')
            recent_entries = self.cursor.fetchall()

            for entry in recent_entries:
                tree.insert('', tk.END, values=entry)

        except Exception as e:
            print(f"خطا در دریافت داده‌ها: {e}")

    def create_employee_form(self, parent):
        """ایجاد فرم ثبت کارمند"""
        form_frame = tk.Frame(parent, bg=self.colors['content_bg'], padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)

        # اسکرول‌بار
        canvas = tk.Canvas(form_frame, bg=self.colors['content_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['content_bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        fields_frame = tk.Frame(scrollable_frame, bg=self.colors['content_bg'])
        fields_frame.pack(fill='both', expand=True)

        row = 0

        # نام
        tk.Label(fields_frame, text="نام:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_first_name_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.emp_first_name_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # نام خانوادگی
        tk.Label(fields_frame, text="نام خانوادگی:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_last_name_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.emp_last_name_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # کد ملی
        tk.Label(fields_frame, text="کد ملی:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_national_id_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.emp_national_id_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تاریخ تولد
        tk.Label(fields_frame, text="تاریخ تولد:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_birth_date = DateEntry(fields_frame, font=self.fonts['normal'],
                                        width=30, background='darkblue',
                                        foreground='white', borderwidth=2,
                                        date_pattern='yyyy-mm-dd')
        self.emp_birth_date.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # آدرس
        tk.Label(fields_frame, text="آدرس:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_address_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.emp_address_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # شماره تماس
        tk.Label(fields_frame, text="شماره تماس:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_phone_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.emp_phone_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # سمت
        tk.Label(fields_frame, text="سمت:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_position_combo = ttk.Combobox(fields_frame,
                                               values=["دوزنده", "برشکار", "بسته‌بند", "انباردار", "مدیر"],
                                               font=self.fonts['normal'], width=28, state='readonly')
        self.emp_position_combo.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تاریخ استخدام
        tk.Label(fields_frame, text="تاریخ استخدام:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_hire_date = DateEntry(fields_frame, font=self.fonts['normal'],
                                       width=30, background='darkblue',
                                       foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd')
        self.emp_hire_date.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # حقوق
        tk.Label(fields_frame, text="حقوق (ریال):",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_salary_entry = tk.Entry(fields_frame, font=self.fonts['normal'], width=30)
        self.emp_salary_entry.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # وضعیت
        tk.Label(fields_frame, text="وضعیت:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.emp_status_var = tk.StringVar(value="فعال")
        status_frame = tk.Frame(fields_frame, bg=self.colors['content_bg'])
        status_frame.grid(row=row, column=1, sticky='w', pady=10, padx=5)

        tk.Radiobutton(status_frame, text="فعال", variable=self.emp_status_var,
                       value="فعال", bg=self.colors['content_bg'],
                       font=self.fonts['normal']).pack(side='left', padx=10)
        tk.Radiobutton(status_frame, text="غیرفعال", variable=self.emp_status_var,
                       value="غیرفعال", bg=self.colors['content_bg'],
                       font=self.fonts['normal']).pack(side='left', padx=10)
        row += 1

        # توضیحات
        tk.Label(fields_frame, text="توضیحات:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='nw', pady=10, padx=5)
        self.emp_notes_text = tk.Text(fields_frame, font=self.fonts['normal'],
                                      width=30, height=4)
        self.emp_notes_text.grid(row=row, column=1, sticky='w', pady=10, padx=5)

        fields_frame.columnconfigure(1, weight=1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # دکمه‌ها
        buttons_frame = tk.Frame(parent, bg=self.colors['content_bg'])
        buttons_frame.pack(fill='x', pady=10)

        tk.Button(buttons_frame, text="💾 ثبت کارمند",
                  bg=self.colors['success'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=30,
                  pady=10,
                  command=self.save_employee).pack(side='right', padx=10)

        tk.Button(buttons_frame, text="🧹 پاک کردن فرم",
                  bg=self.colors['warning'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=30,
                  pady=10,
                  command=self.clear_employee_form).pack(side='right', padx=10)

    def create_employees_table(self, parent):
        """ایجاد جدول کارمندان"""
        # فریم اصلی برای جدول
        table_frame = tk.Frame(parent, bg=self.colors['content_bg'])
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # ایجاد Treeview
        columns = ('id', 'full_name', 'national_id', 'position', 'phone', 'hire_date', 'status')
        self.employees_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # تعریف ستون‌ها
        self.employees_tree.heading('id', text='کد پرسنلی')
        self.employees_tree.heading('full_name', text='نام و نام خانوادگی')
        self.employees_tree.heading('national_id', text='کد ملی')
        self.employees_tree.heading('position', text='سمت')
        self.employees_tree.heading('phone', text='تلفن')
        self.employees_tree.heading('hire_date', text='تاریخ استخدام')
        self.employees_tree.heading('status', text='وضعیت')

        self.employees_tree.column('id', width=80)
        self.employees_tree.column('full_name', width=150)
        self.employees_tree.column('national_id', width=100)
        self.employees_tree.column('position', width=100)
        self.employees_tree.column('phone', width=100)
        self.employees_tree.column('hire_date', width=100)
        self.employees_tree.column('status', width=80)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.employees_tree.yview)
        self.employees_tree.configure(yscroll=scrollbar.set)

        self.employees_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # دکمه‌های مدیریت
        manage_frame = tk.Frame(parent, bg=self.colors['content_bg'])
        manage_frame.pack(fill='x', pady=10)

        tk.Button(manage_frame, text="🔄 بارگذاری مجدد",
                  bg=self.colors['info'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=20,
                  pady=8,
                  command=self.load_employees).pack(side='right', padx=5)

        tk.Button(manage_frame, text="✏️ ویرایش",
                  bg=self.colors['warning'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=20,
                  pady=8,
                  command=self.edit_employee).pack(side='right', padx=5)

        tk.Button(manage_frame, text="🗑️ حذف",
                  bg=self.colors['danger'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=20,
                  pady=8,
                  command=self.delete_employee).pack(side='right', padx=5)

        # بارگذاری اولیه داده‌ها
        self.load_employees()

    def create_entry_search_form(self, parent):
        """ایجاد فرم جستجوی ورودی‌ها"""
        form_frame = tk.Frame(parent, bg=self.colors['content_bg'], padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)

        # فیلدهای جستجو
        search_fields = tk.Frame(form_frame, bg=self.colors['content_bg'])
        search_fields.pack(fill='x', pady=(0, 20))

        row = 0

        # کد محصول
        tk.Label(search_fields, text="کد محصول:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_product_code = tk.Entry(search_fields, font=self.fonts['normal'], width=25)
        self.search_product_code.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # نام محصول
        tk.Label(search_fields, text="نام محصول:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_product_name = tk.Entry(search_fields, font=self.fonts['normal'], width=25)
        self.search_product_name.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # رنگ
        tk.Label(search_fields, text="رنگ:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_color = ttk.Combobox(search_fields, values=self.fabric_colors,
                                         font=self.fonts['normal'], width=23, state='readonly')
        self.search_color.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # سایز
        tk.Label(search_fields, text="سایز:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_size = ttk.Combobox(search_fields, values=self.sizes,
                                        font=self.fonts['normal'], width=23, state='readonly')
        self.search_size.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # نوع پارچه
        tk.Label(search_fields, text="نوع پارچه:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_fabric_type = ttk.Combobox(search_fields, values=self.fabric_types,
                                               font=self.fonts['normal'], width=23, state='readonly')
        self.search_fabric_type.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تاریخ از
        tk.Label(search_fields, text="تاریخ از:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_date_from = DateEntry(search_fields, font=self.fonts['normal'],
                                          width=23, background='darkblue',
                                          foreground='white', borderwidth=2,
                                          date_pattern='yyyy-mm-dd')
        self.search_date_from.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تاریخ تا
        tk.Label(search_fields, text="تاریخ تا:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_date_to = DateEntry(search_fields, font=self.fonts['normal'],
                                        width=23, background='darkblue',
                                        foreground='white', borderwidth=2,
                                        date_pattern='yyyy-mm-dd')
        self.search_date_to.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # نام دوزنده
        tk.Label(search_fields, text="نام دوزنده:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.search_tailor = tk.Entry(search_fields, font=self.fonts['normal'], width=25)
        self.search_tailor.grid(row=row, column=1, sticky='w', pady=10, padx=5)

        search_fields.columnconfigure(1, weight=1)

        # دکمه جستجو
        tk.Button(form_frame, text="🔍 اجرای جستجو",
                  bg=self.colors['info'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=30,
                  pady=10,
                  command=self.search_entries).pack(pady=10)

        # فریم نتایج
        results_frame = tk.Frame(form_frame, bg=self.colors['content_bg'])
        results_frame.pack(fill='both', expand=True, pady=20)

        # ایجاد Treeview برای نتایج
        columns = ('id', 'product_code', 'product_name', 'color', 'size', 'fabric_type', 'entry_date', 'tailor')
        self.search_results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)

        # تعریف ستون‌ها
        self.search_results_tree.heading('id', text='شناسه')
        self.search_results_tree.heading('product_code', text='کد محصول')
        self.search_results_tree.heading('product_name', text='نام محصول')
        self.search_results_tree.heading('color', text='رنگ')
        self.search_results_tree.heading('size', text='سایز')
        self.search_results_tree.heading('fabric_type', text='نوع پارچه')
        self.search_results_tree.heading('entry_date', text='تاریخ ورود')
        self.search_results_tree.heading('tailor', text='دوزنده')

        self.search_results_tree.column('id', width=50)
        self.search_results_tree.column('product_code', width=100)
        self.search_results_tree.column('product_name', width=120)
        self.search_results_tree.column('color', width=80)
        self.search_results_tree.column('size', width=80)
        self.search_results_tree.column('fabric_type', text='نوع پارچه', width=100)
        self.search_results_tree.column('entry_date', text='تاریخ ورود', width=100)
        self.search_results_tree.column('tailor', text='دوزنده', width=100)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_results_tree.yview)
        self.search_results_tree.configure(yscroll=scrollbar.set)

        self.search_results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_output_search_form(self, parent):
        """ایجاد فرم جستجوی خروجی‌ها"""
        form_frame = tk.Frame(parent, bg=self.colors['content_bg'], padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)

        # فیلدهای جستجو (مشابه ورودی با اضافات)
        search_fields = tk.Frame(form_frame, bg=self.colors['content_bg'])
        search_fields.pack(fill='x', pady=(0, 20))

        row = 0

        # کد محصول
        tk.Label(search_fields, text="کد محصول:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_search_code = tk.Entry(search_fields, font=self.fonts['normal'], width=25)
        self.output_search_code.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # کیفیت
        tk.Label(search_fields, text="کیفیت:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_search_quality = ttk.Combobox(search_fields, values=self.qualities,
                                                  font=self.fonts['normal'], width=23, state='readonly')
        self.output_search_quality.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تاریخ خروج از
        tk.Label(search_fields, text="تاریخ خروج از:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_search_date_from = DateEntry(search_fields, font=self.fonts['normal'],
                                                 width=23, background='darkblue',
                                                 foreground='white', borderwidth=2,
                                                 date_pattern='yyyy-mm-dd')
        self.output_search_date_from.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # تاریخ خروج تا
        tk.Label(search_fields, text="تاریخ خروج تا:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_search_date_to = DateEntry(search_fields, font=self.fonts['normal'],
                                               width=23, background='darkblue',
                                               foreground='white', borderwidth=2,
                                               date_pattern='yyyy-mm-dd')
        self.output_search_date_to.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # مقصد
        tk.Label(search_fields, text="مقصد:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_search_destination = tk.Entry(search_fields, font=self.fonts['normal'], width=25)
        self.output_search_destination.grid(row=row, column=1, sticky='w', pady=10, padx=5)
        row += 1

        # کد بسته‌بندی
        tk.Label(search_fields, text="کد بسته‌بندی:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)
        self.output_search_package = tk.Entry(search_fields, font=self.fonts['normal'], width=25)
        self.output_search_package.grid(row=row, column=1, sticky='w', pady=10, padx=5)

        search_fields.columnconfigure(1, weight=1)

        # دکمه جستجو
        tk.Button(form_frame, text="🔍 اجرای جستجو",
                  bg=self.colors['info'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=30,
                  pady=10,
                  command=self.search_outputs).pack(pady=10)

        # فریم نتایج
        results_frame = tk.Frame(form_frame, bg=self.colors['content_bg'])
        results_frame.pack(fill='both', expand=True, pady=20)

        # ایجاد Treeview برای نتایج
        columns = ('id', 'product_code', 'output_date', 'quality', 'destination', 'quantity', 'package_code')
        self.output_results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)

        # تعریف ستون‌ها
        self.output_results_tree.heading('id', text='شناسه')
        self.output_results_tree.heading('product_code', text='کد محصول')
        self.output_results_tree.heading('output_date', text='تاریخ خروج')
        self.output_results_tree.heading('quality', text='کیفیت')
        self.output_results_tree.heading('destination', text='مقصد')
        self.output_results_tree.heading('quantity', text='تعداد')
        self.output_results_tree.heading('package_code', text='کد بسته')

        self.output_results_tree.column('id', width=50)
        self.output_results_tree.column('product_code', width=100)
        self.output_results_tree.column('output_date', width=100)
        self.output_results_tree.column('quality', width=80)
        self.output_results_tree.column('destination', width=120)
        self.output_results_tree.column('quantity', width=60)
        self.output_results_tree.column('package_code', width=100)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.output_results_tree.yview)
        self.output_results_tree.configure(yscroll=scrollbar.set)

        self.output_results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_combined_search_form(self, parent):
        """ایجاد فرم جستجوی ترکیبی"""
        form_frame = tk.Frame(parent, bg=self.colors['content_bg'], padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)

        tk.Label(form_frame, text="جستجوی ترکیبی در همه داده‌ها",
                 font=self.fonts['subtitle'],
                 bg=self.colors['content_bg']).pack(anchor='w', pady=(0, 20))

        # فیلد جستجوی عمومی
        search_frame = tk.Frame(form_frame, bg=self.colors['content_bg'])
        search_frame.pack(fill='x', pady=(0, 20))

        tk.Label(search_frame, text="عبارت جستجو:",
                 font=self.fonts['normal'],
                 bg=self.colors['content_bg']).pack(side='left', padx=5)

        self.combined_search_entry = tk.Entry(search_frame, font=self.fonts['normal'], width=40)
        self.combined_search_entry.pack(side='left', padx=5)

        tk.Button(search_frame, text="🔍 جستجوی سریع",
                  bg=self.colors['info'],
                  fg='white',
                  font=self.fonts['normal'],
                  padx=20,
                  command=self.combined_search).pack(side='left', padx=5)

        # نوع جستجو
        type_frame = tk.Frame(form_frame, bg=self.colors['content_bg'])
        type_frame.pack(fill='x', pady=(0, 20))

        self.search_type_var = tk.StringVar(value="all")

        tk.Radiobutton(type_frame, text="همه داده‌ها", variable=self.search_type_var,
                       value="all", bg=self.colors['content_bg'],
                       font=self.fonts['normal']).pack(side='left', padx=20)
        tk.Radiobutton(type_frame, text="فقط ورودی‌ها", variable=self.search_type_var,
                       value="entries", bg=self.colors['content_bg'],
                       font=self.fonts['normal']).pack(side='left', padx=20)
        tk.Radiobutton(type_frame, text="فقط خروجی‌ها", variable=self.search_type_var,
                       value="outputs", bg=self.colors['content_bg'],
                       font=self.fonts['normal']).pack(side='left', padx=20)

        # فریم نتایج
        results_frame = tk.Frame(form_frame, bg=self.colors['content_bg'])
        results_frame.pack(fill='both', expand=True)

        # ایجاد Treeview برای نتایج
        columns = ('type', 'code', 'description', 'date', 'details')
        self.combined_results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=12)

        # تعریف ستون‌ها
        self.combined_results_tree.heading('type', text='نوع')
        self.combined_results_tree.heading('code', text='کد')
        self.combined_results_tree.heading('description', text='توضیحات')
        self.combined_results_tree.heading('date', text='تاریخ')
        self.combined_results_tree.heading('details', text='جزئیات')

        self.combined_results_tree.column('type', width=80)
        self.combined_results_tree.column('code', width=100)
        self.combined_results_tree.column('description', width=200)
        self.combined_results_tree.column('date', width=100)
        self.combined_results_tree.column('details', width=150)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.combined_results_tree.yview)
        self.combined_results_tree.configure(yscroll=scrollbar.set)

        self.combined_results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_outputs_table(self, parent):
        """ایجاد جدول خروجی‌ها"""
        # فریم اصلی برای جدول
        table_frame = tk.Frame(parent, bg=self.colors['content_bg'])
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # ایجاد Treeview
        columns = ('id', 'product_code', 'output_date', 'quality', 'destination', 'quantity', 'package_code')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # تعریف ستون‌ها
        tree.heading('id', text='شناسه')
        tree.heading('product_code', text='کد محصول')
        tree.heading('output_date', text='تاریخ خروج')
        tree.heading('quality', text='کیفیت')
        tree.heading('destination', text='مقصد')
        tree.heading('quantity', text='تعداد')
        tree.heading('package_code', text='کد بسته')

        tree.column('id', width=50)
        tree.column('product_code', width=100)
        tree.column('output_date', width=100)
        tree.column('quality', width=80)
        tree.column('destination', width=120)
        tree.column('quantity', width=60)
        tree.column('package_code', width=100)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # بارگذاری داده‌های خروجی
        try:
            self.cursor.execute('''
                                SELECT id, product_code, output_date, quality, destination, quantity, package_code
                                FROM garment_outputs
                                ORDER BY output_date DESC
                                ''')
            outputs = self.cursor.fetchall()

            for output in outputs:
                tree.insert('', tk.END, values=output)

        except Exception as e:
            print(f"خطا در دریافت خروجی‌ها: {e}")

    def create_report_card(self, parent, icon, title, desc, command):
        """ایجاد کارت گزارش"""
        card = tk.Frame(parent, bg='white',
                        highlightbackground=self.colors['border'],
                        highlightthickness=1,
                        cursor='hand2')

        content = tk.Frame(card, bg='white', padx=20, pady=20)
        content.pack(fill='both', expand=True)

        # آیکون
        tk.Label(content, text=icon,
                 font=self.fonts['large'],
                 bg='white').pack(pady=(0, 10))

        # عنوان
        tk.Label(content, text=title,
                 font=self.fonts['subtitle'],
                 bg='white',
                 fg=self.colors['text_dark']).pack(pady=(0, 5))

        # توضیحات
        tk.Label(content, text=desc,
                 font=self.fonts['small'],
                 bg='white',
                 fg=self.colors['text_gray'],
                 wraplength=200).pack(pady=(0, 15))

        # دکمه
        tk.Button(content, text="ایجاد گزارش",
                  bg=self.colors['info'],
                  fg='white',
                  font=self.fonts['normal'],
                  command=command).pack()

        return card

    def create_setting_card(self, parent, icon, title, desc, command):
        """ایجاد کارت تنظیمات"""
        card = tk.Frame(parent, bg='white',
                        highlightbackground=self.colors['border'],
                        highlightthickness=1,
                        cursor='hand2')

        content = tk.Frame(card, bg='white', padx=20, pady=20)
        content.pack(fill='both', expand=True)

        # آیکون
        tk.Label(content, text=icon,
                 font=self.fonts['large'],
                 bg='white').pack(pady=(0, 10))

        # عنوان
        tk.Label(content, text=title,
                 font=self.fonts['subtitle'],
                 bg='white',
                 fg=self.colors['text_dark']).pack(pady=(0, 5))

        # توضیحات
        tk.Label(content, text=desc,
                 font=self.fonts['small'],
                 bg='white',
                 fg=self.colors['text_gray'],
                 wraplength=250).pack(pady=(0, 15))

        # دکمه
        tk.Button(content, text="اجرا",
                  bg=self.colors['sidebar_active'],
                  fg='white',
                  font=self.fonts['normal'],
                  command=command).pack()

        return card

    # ==================== متدهای عملیاتی ====================

    def save_garment_entry(self):
        """ذخیره ورودی پوشاک"""
        try:
            # جمع‌آوری داده‌ها
            product_name = self.product_name_entry.get().strip()
            product_code = self.product_code_entry.get().strip()
            size = self.size_var.get() if self.size_var.get() == "تک سایز" or self.size_var.get() == "سایز 1 و 2" else self.size_combo.get()
            color = self.color_var.get() if self.color_var.get() else self.custom_color_entry.get().strip()
            custom_color = self.custom_color_entry.get().strip() if self.color_var.get() == "" else ""
            fabric_type = self.fabric_type_combo.get()
            cutting_code = self.cutting_code_entry.get().strip()
            entry_date = self.entry_date_entry.get()
            tailor_name = self.tailor_entry.get().strip()
            quantity = int(self.quantity_entry.get())
            notes = self.notes_text.get("1.0", tk.END).strip()

            # اعتبارسنجی
            if not product_name:
                messagebox.showwarning("اخطار", "لطفا نام محصول را وارد کنید")
                return
            if not product_code:
                messagebox.showwarning("اخطار", "لطفا کد محصول را وارد کنید")
                return
            if not color:
                messagebox.showwarning("اخطار", "لطفا رنگ را انتخاب یا وارد کنید")
                return
            if not fabric_type:
                messagebox.showwarning("اخطار", "لطفا نوع پارچه را انتخاب کنید")
                return
            if not cutting_code:
                messagebox.showwarning("اخطار", "لطفا کد برش را وارد کنید")
                return
            if not tailor_name:
                messagebox.showwarning("اخطار", "لطفا نام دوزنده را وارد کنید")
                return

            # بررسی تکراری نبودن کد محصول
            self.cursor.execute("SELECT id FROM garment_entries WHERE product_code = ?", (product_code,))
            if self.cursor.fetchone():
                messagebox.showwarning("اخطار", "کد محصول تکراری است")
                return

            # ذخیره در دیتابیس
            self.cursor.execute('''
                                INSERT INTO garment_entries
                                (product_name, product_code, size, color, custom_color, fabric_type,
                                 cutting_code, entry_date, tailor_name, quantity, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (product_name, product_code, size, color, custom_color, fabric_type,
                                      cutting_code, entry_date, tailor_name, quantity, notes))

            self.conn.commit()

            messagebox.showinfo("موفقیت", "ورودی پوشاک با موفقیت ثبت شد")
            self.clear_garment_form()
            self.update_stats()

        except ValueError as e:
            messagebox.showerror("خطا", f"خطا در مقادیر ورودی: {str(e)}")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ثبت اطلاعات: {str(e)}")

    def clear_garment_form(self):
        """پاک کردن فرم ورودی پوشاک"""
        self.product_name_entry.delete(0, tk.END)
        self.product_code_entry.delete(0, tk.END)
        self.size_var.set("تک سایز")
        self.color_var.set("")
        self.custom_color_entry.delete(0, tk.END)
        self.fabric_type_combo.set("")
        self.cutting_code_entry.delete(0, tk.END)
        self.entry_date_entry.set_date(datetime.now())
        self.tailor_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")
        self.notes_text.delete("1.0", tk.END)

    def save_garment_output(self):
        """ذخیره خروجی کارگاه"""
        try:
            product_code = self.output_product_code.get()
            output_date = self.output_date_entry.get()
            quality = self.quality_var.get()
            destination = self.destination_entry.get().strip()
            quantity = int(self.output_quantity.get())
            package_code = self.package_code_entry.get().strip()
            notes = self.output_notes_entry.get().strip()

            # اعتبارسنجی
            if not product_code:
                messagebox.showwarning("اخطار", "لطفا محصول را انتخاب کنید")
                return
            if not quality:
                messagebox.showwarning("اخطار", "لطفا کیفیت را انتخاب کنید")
                return

            # بررسی موجودی
            self.cursor.execute('''
                                SELECT quantity
                                FROM garment_entries
                                WHERE product_code = ?
                                ''', (product_code,))
            entry = self.cursor.fetchone()

            if not entry:
                messagebox.showwarning("اخطار", "محصول مورد نظر یافت نشد")
                return

            available_quantity = entry[0]

            # کم کردن از موجودی
            if quantity > available_quantity:
                messagebox.showwarning("اخطار", f"موجودی کافی نیست. موجودی: {available_quantity}")
                return

            new_quantity = available_quantity - quantity

            # ذخیره خروجی
            self.cursor.execute('''
                                INSERT INTO garment_outputs
                                (product_code, output_date, quality, destination, quantity, package_code, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (product_code, output_date, quality, destination, quantity, package_code, notes))

            # به‌روزرسانی موجودی
            self.cursor.execute('''
                                UPDATE garment_entries
                                SET quantity = ?
                                WHERE product_code = ?
                                ''', (new_quantity, product_code))

            self.conn.commit()

            messagebox.showinfo("موفقیت", "خروجی با موفقیت ثبت شد")
            self.clear_output_form()
            self.update_stats()

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ثبت خروجی: {str(e)}")

    def clear_output_form(self):
        """پاک کردن فرم خروجی"""
        self.output_product_code.set("")
        self.output_date_entry.set_date(datetime.now())
        self.quality_var.set("")
        self.destination_entry.delete(0, tk.END)
        self.output_quantity.delete(0, tk.END)
        self.output_quantity.insert(0, "1")
        self.package_code_entry.delete(0, tk.END)
        self.output_notes_entry.delete(0, tk.END)

    def search_product_for_output(self):
        """جستجوی محصول برای خروجی"""
        search_term = self.output_search_entry.get().strip()

        if not search_term:
            messagebox.showwarning("اخطار", "لطفا عبارت جستجو را وارد کنید")
            return

        try:
            # پاک کردن نتایج قبلی
            for widget in self.output_results_frame.winfo_children():
                widget.destroy()

            # جستجو در دیتابیس
            self.cursor.execute('''
                                SELECT product_code, product_name, color, size, quantity
                                FROM garment_entries
                                WHERE product_code LIKE ? OR product_name LIKE ?
                                ORDER BY product_name
                                ''', (f'%{search_term}%', f'%{search_term}%'))

            results = self.cursor.fetchall()

            if not results:
                tk.Label(self.output_results_frame, text="نتیجه‌ای یافت نشد",
                         bg=self.colors['content_bg'],
                         font=self.fonts['normal']).pack()
                return

            # نمایش نتایج
            for i, (code, name, color, size, quantity) in enumerate(results):
                result_frame = tk.Frame(self.output_results_frame, bg=self.colors['content_bg'])
                result_frame.pack(fill='x', pady=2)

                tk.Label(result_frame, text=f"{code} - {name} ({color} - {size}) - موجودی: {quantity}",
                         bg=self.colors['content_bg'],
                         font=self.fonts['normal']).pack(side='left')

                tk.Button(result_frame, text="انتخاب",
                          bg=self.colors['info'],
                          fg='white',
                          font=self.fonts['small'],
                          command=lambda c=code: self.select_product_for_output(c)).pack(side='right')

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در جستجو: {str(e)}")

    def select_product_for_output(self, product_code):
        """انتخاب محصول برای خروجی"""
        self.output_product_code.set(product_code)
        self.output_search_entry.delete(0, tk.END)

        # پاک کردن نتایج جستجو
        for widget in self.output_results_frame.winfo_children():
            widget.destroy()

    def save_employee(self):
        """ذخیره اطلاعات کارمند"""
        try:
            first_name = self.emp_first_name_entry.get().strip()
            last_name = self.emp_last_name_entry.get().strip()
            national_id = self.emp_national_id_entry.get().strip()
            birth_date = self.emp_birth_date.get()
            address = self.emp_address_entry.get().strip()
            phone = self.emp_phone_entry.get().strip()
            position = self.emp_position_combo.get()
            hire_date = self.emp_hire_date.get()
            salary = self.emp_salary_entry.get().strip()
            status = self.emp_status_var.get()
            notes = self.emp_notes_text.get("1.0", tk.END).strip()

            # اعتبارسنجی
            if not first_name or not last_name:
                messagebox.showwarning("اخطار", "لطفا نام و نام خانوادگی را وارد کنید")
                return
            if not phone:
                messagebox.showwarning("اخطار", "لطفا شماره تماس را وارد کنید")
                return

            # تبدیل حقوق به عدد
            salary_value = float(salary) if salary else 0.0

            # ذخیره در دیتابیس
            self.cursor.execute('''
                                INSERT INTO employees
                                (first_name, last_name, national_id, birth_date, address, phone,
                                 position, hire_date, salary, status, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (first_name, last_name, national_id, birth_date, address, phone,
                                      position, hire_date, salary_value, status, notes))

            self.conn.commit()

            messagebox.showinfo("موفقیت", "اطلاعات کارمند با موفقیت ثبت شد")
            self.clear_employee_form()
            self.load_employees()  # بارگذاری مجدد لیست
            self.update_stats()

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ثبت اطلاعات: {str(e)}")

    def clear_employee_form(self):
        """پاک کردن فرم کارمند"""
        self.emp_first_name_entry.delete(0, tk.END)
        self.emp_last_name_entry.delete(0, tk.END)
        self.emp_national_id_entry.delete(0, tk.END)
        self.emp_birth_date.set_date(datetime.now())
        self.emp_address_entry.delete(0, tk.END)
        self.emp_phone_entry.delete(0, tk.END)
        self.emp_position_combo.set("")
        self.emp_hire_date.set_date(datetime.now())
        self.emp_salary_entry.delete(0, tk.END)
        self.emp_status_var.set("فعال")
        self.emp_notes_text.delete("1.0", tk.END)

    def load_employees(self):
        """بارگذاری لیست کارمندان"""
        try:
            # پاک کردن داده‌های قبلی
            for item in self.employees_tree.get_children():
                self.employees_tree.delete(item)

            # دریافت داده‌ها از دیتابیس
            self.cursor.execute('''
                                SELECT id,
                                       first_name || ' ' || last_name,
                                       national_id,
                                       position,
                                       phone,
                                       hire_date,
                                       status
                                FROM employees
                                ORDER BY last_name, first_name
                                ''')
            employees = self.cursor.fetchall()

            for emp in employees:
                self.employees_tree.insert('', tk.END, values=emp)

        except Exception as e:
            print(f"خطا در بارگذاری کارمندان: {e}")

    def edit_employee(self):
        """ویرایش کارمند"""
        selected_item = self.employees_tree.selection()
        if not selected_item:
            messagebox.showwarning("اخطار", "لطفا یک کارمند را انتخاب کنید")
            return

        item = self.employees_tree.item(selected_item[0])
        emp_id = item['values'][0]

        messagebox.showinfo("ویرایش", f"ویرایش کارمند با کد پرسنلی: {emp_id}")
        # در اینجا می‌توانید فرم ویرایش را باز کنید

    def delete_employee(self):
        """حذف کارمند"""
        selected_item = self.employees_tree.selection()
        if not selected_item:
            messagebox.showwarning("اخطار", "لطفا یک کارمند را انتخاب کنید")
            return

        item = self.employees_tree.item(selected_item[0])
        emp_id = item['values'][0]
        emp_name = item['values'][1]

        if messagebox.askyesno("تأیید حذف", f"آیا از حذف کارمند '{emp_name}' مطمئن هستید؟"):
            try:
                self.cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
                self.conn.commit()

                messagebox.showinfo("موفقیت", "کارمند با موفقیت حذف شد")
                self.load_employees()
                self.update_stats()

            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف کارمند: {str(e)}")

    def search_entries(self):
        """جستجوی ورودی‌ها"""
        try:
            # جمع‌آوری پارامترهای جستجو
            params = []
            conditions = []

            product_code = self.search_product_code.get().strip()
            if product_code:
                conditions.append("product_code LIKE ?")
                params.append(f'%{product_code}%')

            product_name = self.search_product_name.get().strip()
            if product_name:
                conditions.append("product_name LIKE ?")
                params.append(f'%{product_name}%')

            color = self.search_color.get()
            if color:
                conditions.append("(color = ? OR custom_color = ?)")
                params.extend([color, color])

            size = self.search_size.get()
            if size:
                conditions.append("size = ?")
                params.append(size)

            fabric_type = self.search_fabric_type.get()
            if fabric_type:
                conditions.append("fabric_type = ?")
                params.append(fabric_type)

            date_from = self.search_date_from.get()
            date_to = self.search_date_to.get()
            if date_from:
                conditions.append("entry_date >= ?")
                params.append(date_from)
            if date_to:
                conditions.append("entry_date <= ?")
                params.append(date_to)

            tailor = self.search_tailor.get().strip()
            if tailor:
                conditions.append("tailor_name LIKE ?")
                params.append(f'%{tailor}%')

            # ساخت کوئری
            query = "SELECT id, product_code, product_name, color, size, fabric_type, entry_date, tailor_name FROM garment_entries"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY entry_date DESC"

            # اجرای جستجو
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            # پاک کردن نتایج قبلی
            for item in self.search_results_tree.get_children():
                self.search_results_tree.delete(item)

            # نمایش نتایج
            for result in results:
                self.search_results_tree.insert('', tk.END, values=result)

            if not results:
                messagebox.showinfo("جستجو", "نتیجه‌ای یافت نشد")

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در جستجو: {str(e)}")

    def search_outputs(self):
        """جستجوی خروجی‌ها"""
        try:
            # جمع‌آوری پارامترهای جستجو
            params = []
            conditions = []

            product_code = self.output_search_code.get().strip()
            if product_code:
                conditions.append("product_code LIKE ?")
                params.append(f'%{product_code}%')

            quality = self.output_search_quality.get()
            if quality:
                conditions.append("quality = ?")
                params.append(quality)

            date_from = self.output_search_date_from.get()
            date_to = self.output_search_date_to.get()
            if date_from:
                conditions.append("output_date >= ?")
                params.append(date_from)
            if date_to:
                conditions.append("output_date <= ?")
                params.append(date_to)

            destination = self.output_search_destination.get().strip()
            if destination:
                conditions.append("destination LIKE ?")
                params.append(f'%{destination}%')

            package = self.output_search_package.get().strip()
            if package:
                conditions.append("package_code LIKE ?")
                params.append(f'%{package}%')

            # ساخت کوئری
            query = "SELECT id, product_code, output_date, quality, destination, quantity, package_code FROM garment_outputs"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY output_date DESC"

            # اجرای جستجو
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            # پاک کردن نتایج قبلی
            for item in self.output_results_tree.get_children():
                self.output_results_tree.delete(item)

            # نمایش نتایج
            for result in results:
                self.output_results_tree.insert('', tk.END, values=result)

            if not results:
                messagebox.showinfo("جستجو", "نتیجه‌ای یافت نشد")

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در جستجو: {str(e)}")

    def combined_search(self):
        """جستجوی ترکیبی"""
        search_term = self.combined_search_entry.get().strip()
        search_type = self.search_type_var.get()

        if not search_term:
            messagebox.showwarning("اخطار", "لطفا عبارت جستجو را وارد کنید")
            return

        try:
            # پاک کردن نتایج قبلی
            for item in self.combined_results_tree.get_children():
                self.combined_results_tree.delete(item)

            results = []

            # جستجو در ورودی‌ها
            if search_type in ["all", "entries"]:
                self.cursor.execute('''
                                    SELECT 'ورودی'                        as type,
                                           product_code                   as code,
                                           product_name || ' - ' || color as description,
                                           entry_date as date, 'دوزنده: ' || tailor_name as details
                                    FROM garment_entries
                                    WHERE product_code LIKE ?
                                       OR product_name LIKE ?
                                       OR color LIKE ?
                                       OR tailor_name LIKE ?
                                       OR fabric_type LIKE ?
                                    ORDER BY entry_date DESC
                                    ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%',
                                          f'%{search_term}%', f'%{search_term}%'))

                results.extend(self.cursor.fetchall())

            # جستجو در خروجی‌ها
            if search_type in ["all", "outputs"]:
                self.cursor.execute('''
                                    SELECT 'خروجی'                         as type,
                                           product_code                    as code,
                                           quality || ' - ' || destination as description,
                                           output_date as date, 'کد بسته: ' || COALESCE(package_code, 'ندارد') as details
                                    FROM garment_outputs
                                    WHERE product_code LIKE ?
                                       OR quality LIKE ?
                                       OR destination LIKE ?
                                       OR package_code LIKE ?
                                    ORDER BY output_date DESC
                                    ''', (f'%{search_term}%', f'%{search_term}%',
                                          f'%{search_term}%', f'%{search_term}%'))

                results.extend(self.cursor.fetchall())

            # جستجو در کارمندان
            if search_type == "all":
                self.cursor.execute('''
                                    SELECT 'کارمند'                       as type,
                                           national_id                    as code,
                                           first_name || ' ' || last_name as description,
                                           hire_date as date, position as details
                                    FROM employees
                                    WHERE first_name LIKE ?
                                       OR last_name LIKE ?
                                       OR national_id LIKE ?
                                       OR position LIKE ?
                                       OR phone LIKE ?
                                    ORDER BY last_name, first_name
                                    ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%',
                                          f'%{search_term}%', f'%{search_term}%'))

                results.extend(self.cursor.fetchall())

            # نمایش نتایج
            for result in results:
                self.combined_results_tree.insert('', tk.END, values=result)

            if not results:
                messagebox.showinfo("جستجو", "نتیجه‌ای یافت نشد")

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در جستجو: {str(e)}")

    # ==================== متدهای گزارش‌گیری ====================

    def generate_daily_report(self):
        """تولید گزارش روزانه"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            # تعداد ورودی‌های امروز
            self.cursor.execute('''
                                SELECT COUNT(*), SUM(quantity)
                                FROM garment_entries
                                WHERE entry_date = ?
                                ''', (today,))
            entries_today = self.cursor.fetchone()

            # تعداد خروجی‌های امروز
            self.cursor.execute('''
                                SELECT COUNT(*), SUM(quantity)
                                FROM garment_outputs
                                WHERE output_date = ?
                                ''', (today,))
            outputs_today = self.cursor.fetchone()

            # نمایش گزارش
            report = f"📊 گزارش روزانه ({today})\n\n"
            report += f"📥 ورودی‌های امروز:\n"
            report += f"   تعداد رکورد: {entries_today[0] or 0}\n"
            report += f"   تعداد محصولات: {entries_today[1] or 0}\n\n"
            report += f"📤 خروجی‌های امروز:\n"
            report += f"   تعداد رکورد: {outputs_today[0] or 0}\n"
            report += f"   تعداد محصولات: {outputs_today[1] or 0}"

            messagebox.showinfo("گزارش روزانه", report)

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تولید گزارش: {str(e)}")

    def generate_monthly_report(self):
        """تولید گزارش ماهانه"""
        try:
            current_month = datetime.now().strftime("%Y-%m")

            # آمار ورودی‌های ماه
            self.cursor.execute('''
                                SELECT COUNT(*), SUM(quantity)
                                FROM garment_entries
                                WHERE strftime('%Y-%m', entry_date) = ?
                                ''', (current_month,))
            entries_month = self.cursor.fetchone()

            # آمار خروجی‌های ماه
            self.cursor.execute('''
                                SELECT COUNT(*), SUM(quantity)
                                FROM garment_outputs
                                WHERE strftime('%Y-%m', output_date) = ?
                                ''', (current_month,))
            outputs_month = self.cursor.fetchone()

            # آمار کارمندان
            self.cursor.execute('''
                                SELECT COUNT(*)
                                FROM employees
                                WHERE status = 'فعال'
                                ''')
            active_employees = self.cursor.fetchone()[0]

            # نمایش گزارش
            report = f"📈 گزارش ماهانه ({current_month})\n\n"
            report += f"📥 ورودی‌های ماه:\n"
            report += f"   تعداد رکورد: {entries_month[0] or 0}\n"
            report += f"   تعداد محصولات: {entries_month[1] or 0}\n\n"
            report += f"📤 خروجی‌های ماه:\n"
            report += f"   تعداد رکورد: {outputs_month[0] or 0}\n"
            report += f"   تعداد محصولات: {outputs_month[1] or 0}\n\n"
            report += f"👥 کارمندان فعال: {active_employees}"

            messagebox.showinfo("گزارش ماهانه", report)

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تولید گزارش: {str(e)}")

    def generate_inventory_report(self):
        """تولید گزارش موجودی"""
        try:
            # موجودی بر اساس رنگ و سایز
            self.cursor.execute('''
                                SELECT color, size, SUM (quantity) as total
                                FROM garment_entries
                                GROUP BY color, size
                                ORDER BY color, size
                                ''')
            inventory = self.cursor.fetchall()

            # ساخت گزارش
            report = "📊 گزارش موجودی انبار\n\n"
            report += "رنگ\t\tسایز\t\tموجودی\n"
            report += "─" * 40 + "\n"

            for color, size, total in inventory:
                report += f"{color[:10]:10}\t{size[:10]:10}\t{total}\n"

            # کل موجودی
            self.cursor.execute('SELECT SUM(quantity) FROM garment_entries')
            total_inventory = self.cursor.fetchone()[0] or 0

            report += f"\n💰 کل موجودی انبار: {total_inventory} عدد"

            messagebox.showinfo("گزارش موجودی", report)

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تولید گزارش: {str(e)}")

    def generate_employee_report(self):
        """تولید گزارش کارمندان"""
        try:
            self.cursor.execute('''
                                SELECT position, status, COUNT(*) as count
                                FROM employees
                                GROUP BY position, status
                                ORDER BY position
                                ''')
            employee_stats = self.cursor.fetchall()

            # ساخت گزارش
            report = "👥 گزارش کارمندان\n\n"
            report += "سمت\t\t\tوضعیت\t\tتعداد\n"
            report += "─" * 50 + "\n"

            for position, status, count in employee_stats:
                report += f"{position[:15]:15}\t{status[:10]:10}\t{count}\n"

            # کل کارمندان
            self.cursor.execute('SELECT COUNT(*) FROM employees')
            total_employees = self.cursor.fetchone()[0] or 0

            report += f"\n👥 کل کارمندان: {total_employees} نفر"

            messagebox.showinfo("گزارش کارمندان", report)

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تولید گزارش: {str(e)}")

    def generate_quality_report(self):
        """تولید گزارش کیفیت"""
        try:
            self.cursor.execute('''
                                SELECT quality, COUNT(*) as count, SUM(quantity) as total
                                FROM garment_outputs
                                GROUP BY quality
                                ORDER BY quality
                                ''')
            quality_stats = self.cursor.fetchall()

            # ساخت گزارش
            report = "🏆 گزارش کیفیت محصولات\n\n"
            report += "کیفیت\t\t\tتعداد رکورد\tتعداد محصولات\n"
            report += "─" * 50 + "\n"

            for quality, count, total in quality_stats:
                report += f"{quality[:15]:15}\t{count:10}\t{total or 0:12}\n"

            # کل خروجی‌ها
            self.cursor.execute('SELECT SUM(quantity) FROM garment_outputs')
            total_outputs = self.cursor.fetchone()[0] or 0

            report += f"\n📤 کل محصولات خروجی: {total_outputs} عدد"

            messagebox.showinfo("گزارش کیفیت", report)

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تولید گزارش: {str(e)}")

    def export_to_excel(self):
        """خروجی اکسل از داده‌ها"""
        try:
            # انتخاب مسیر ذخیره
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="گزارش_کارگاه.csv"
            )

            if not file_path:
                return

            # جمع‌آوری همه داده‌ها
            import csv

            # نوشتن داده‌های ورودی
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)

                # هدر ورودی‌ها
                writer.writerow(["📥 لیست ورودی‌های پوشاک"])
                writer.writerow([])
                writer.writerow(["کد محصول", "نام محصول", "رنگ", "سایز", "نوع پارچه",
                                 "کد برش", "تاریخ ورود", "دوزنده", "تعداد", "توضیحات"])

                self.cursor.execute('SELECT * FROM garment_entries')
                for row in self.cursor.fetchall():
                    writer.writerow(row[1:])  # حذف id

                writer.writerow([])
                writer.writerow([])

                # هدر خروجی‌ها
                writer.writerow(["📤 لیست خروجی‌های پوشاک"])
                writer.writerow([])
                writer.writerow(["کد محصول", "تاریخ خروج", "کیفیت", "مقصد", "تعداد",
                                 "کد بسته", "توضیحات"])

                self.cursor.execute('SELECT * FROM garment_outputs')
                for row in self.cursor.fetchall():
                    writer.writerow(row[2:])  # حذف id و garment_id

                writer.writerow([])
                writer.writerow([])

                # هدر کارمندان
                writer.writerow(["👥 لیست کارمندان"])
                writer.writerow([])
                writer.writerow(["نام", "نام خانوادگی", "کد ملی", "تاریخ تولد", "آدرس",
                                 "تلفن", "سمت", "تاریخ استخدام", "حقوق", "وضعیت", "توضیحات"])

                self.cursor.execute('SELECT * FROM employees')
                for row in self.cursor.fetchall():
                    writer.writerow(row[1:])  # حذف id

            messagebox.showinfo("موفقیت", f"داده‌ها با موفقیت در فایل ذخیره شد:\n{file_path}")

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در خروجی گرفتن: {str(e)}")

    # ==================== متدهای تنظیمات ====================

    def backup_data(self):
        """پشتیبان‌گیری از داده‌ها"""
        try:
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialfile="backup_garment_factory.db"
            )

            if file_path:
                import shutil
                shutil.copy2('garment_factory.db', file_path)
                messagebox.showinfo("موفقیت", f"پشتیبان با موفقیت ایجاد شد:\n{file_path}")

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در پشتیبان‌گیری: {str(e)}")

    def restore_data(self):
        """بازیابی داده‌ها"""
        if messagebox.askyesno("تأیید", "آیا از بازیابی داده‌ها مطمئن هستید؟\nداده‌های فعلی از بین می‌روند."):
            try:
                from tkinter import filedialog
                file_path = filedialog.askopenfilename(
                    filetypes=[("Database files", "*.db"), ("All files", "*.*")]
                )

                if file_path:
                    import shutil
                    self.conn.close()
                    shutil.copy2(file_path, 'garment_factory.db')

                    # راه‌اندازی مجدد دیتابیس
                    self.setup_database()
                    messagebox.showinfo("موفقیت", "داده‌ها با موفقیت بازیابی شدند")
                    self.update_stats()

            except Exception as e:
                messagebox.showerror("خطا", f"خطا در بازیابی: {str(e)}")

    def clean_old_data(self):
        """پاکسازی داده‌های قدیمی"""
        if messagebox.askyesno("تأیید", "آیا از پاکسازی داده‌های قدیمی مطمئن هستید؟"):
            try:
                # حذف داده‌های قدیمی‌تر از 1 سال
                cutoff_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

                self.cursor.execute('DELETE FROM garment_entries WHERE entry_date < ?', (cutoff_date,))
                self.cursor.execute('DELETE FROM garment_outputs WHERE output_date < ?', (cutoff_date,))

                self.conn.commit()

                deleted_count = self.cursor.rowcount
                messagebox.showinfo("موفقیت", f"{deleted_count} رکورد قدیمی پاکسازی شد")
                self.update_stats()

            except Exception as e:
                messagebox.showerror("خطا", f"خطا در پاکسازی: {str(e)}")

    def system_settings(self):
        """تنظیمات سیستم"""
        messagebox.showinfo("تنظیمات", "این بخش در حال توسعه است")

    # ==================== متدهای کمکی ====================

    def get_total_entries(self):
        """دریافت تعداد کل ورودی‌ها"""
        self.cursor.execute("SELECT COUNT(*) FROM garment_entries")
        return self.cursor.fetchone()[0] or 0

    def get_total_outputs(self):
        """دریافت تعداد کل خروجی‌ها"""
        self.cursor.execute("SELECT COUNT(*) FROM garment_outputs")
        return self.cursor.fetchone()[0] or 0

    def get_total_employees(self):
        """دریافت تعداد کل کارمندان"""
        self.cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'فعال'")
        return self.cursor.fetchone()[0] or 0

    def get_inventory_count(self):
        """دریافت تعداد موجودی انبار"""
        self.cursor.execute("SELECT SUM(quantity) FROM garment_entries")
        result = self.cursor.fetchone()[0]
        return result or 0

    def update_stats(self):
        """به‌روزرسانی آمار"""
        try:
            # آمار امروز
            today = datetime.now().strftime("%Y-%m-%d")

            self.cursor.execute('''
                                SELECT COUNT(*)
                                FROM garment_entries
                                WHERE entry_date = ?
                                ''', (today,))
            today_entries = self.cursor.fetchone()[0] or 0

            self.cursor.execute('''
                                SELECT COUNT(*)
                                FROM garment_outputs
                                WHERE output_date = ?
                                ''', (today,))
            today_outputs = self.cursor.fetchone()[0] or 0

            # به‌روزرسانی لیبل‌ها
            self.stats_labels["ورودی امروز"].config(text=str(today_entries))
            self.stats_labels["خروجی امروز"].config(text=str(today_outputs))
            self.stats_labels["کارمندان فعال"].config(text=str(self.get_total_employees()))
            self.stats_labels["موجودی انبار"].config(text=str(self.get_inventory_count()))

        except Exception as e:
            print(f"خطا در به‌روزرسانی آمار: {e}")

    def toggle_fullscreen(self):
        """تغییر حالت فول اسکرین"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

        # تغییر آیکون دکمه
        if self.is_fullscreen:
            self.fullscreen_btn.config(text="⛶")
        else:
            self.fullscreen_btn.config(text="⛶")

    def exit_app(self):
        """خروج از برنامه"""
        if messagebox.askyesno("خروج", "آیا از برنامه خارج می‌شوید؟"):
            self.conn.close()
            self.root.quit()

    def bind_events(self):
        """اتصال رویدادها"""

        # به‌روزرسانی زمان
        def update_time():
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.config(text=current_time)
            self.root.after(1000, update_time)

        update_time()

        # کلیدهای میانبر
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        self.root.bind('<Alt-F4>', lambda e: self.exit_app())

    def run(self):
        """اجرای برنامه"""
        # به‌روزرسانی اولیه آمار
        self.update_stats()

        self.root.mainloop()


# ==================== اجرای برنامه ====================

if __name__ == "__main__":
    # اضافه کردن timedelta برای پاکسازی داده‌ها
    from datetime import timedelta

    app = GarmentPackagingManager()
    app.run()