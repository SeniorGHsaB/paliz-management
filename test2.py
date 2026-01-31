import tkinter as tk
from tkinter import ttk, font, messagebox, simpledialog, filedialog
import ctypes
from datetime import datetime
import json
import os
import sqlite3
from tkinter import scrolledtext

# تنظیم DPI برای ویندوز
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class BusinessManagementApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("نرم افزار مدیریت کسب و کار")

        # تنظیم فول اسکرین
        self.is_fullscreen = True
        self.root.attributes('-fullscreen', True)

        # رنگ‌های ویندوز 11
        self.colors = {
            'bg': '#f3f3f3',
            'title_bar': '#202020',
            'title_bar_light': '#2d2d2d',
            'sidebar': '#fafafa',
            'button_primary': '#0078d4',
            'button_primary_hover': '#106ebe',
            'button_secondary': '#6c757d',
            'button_secondary_hover': '#5a6268',
            'button_success': '#28a745',
            'button_success_hover': '#218838',
            'button_danger': '#dc3545',
            'button_danger_hover': '#c82333',
            'button_warning': '#ffc107',
            'button_warning_hover': '#e0a800',
            'card_bg': '#ffffff',
            'card_border': '#e0e0e0',
            'text_primary': '#000000',
            'text_secondary': '#6c757d',
            'text_light': '#ffffff',
            'accent': '#0078d4',
            'hover_bg': '#f5f5f5',
            'input_bg': '#ffffff'
        }

        # متغیرهای برنامه
        self.current_page = "dashboard"
        self.db_connection = None
        self.employee_data = []
        self.entry_data = []

        self.setup_fonts()
        self.setup_ui()
        self.bind_events()

        # ایجاد دیتابیس نمونه
        self.create_sample_database()

    def setup_fonts(self):
        """تنظیم فونت‌ها"""
        self.fonts = {
            'title': font.Font(family="Segoe UI", size=18, weight="bold"),
            'subtitle': font.Font(family="Segoe UI", size=14, weight="bold"),
            'normal': font.Font(family="Segoe UI", size=11),
            'small': font.Font(family="Segoe UI", size=9),
            'large': font.Font(family="Segoe UI", size=16),
            'icon': font.Font(family="Segoe MDL2 Assets", size=12)
        }

    def setup_ui(self):
        """ایجاد رابط کاربری"""
        # Title Bar
        self.create_title_bar()

        # Main Container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True)

        # Sidebar با منوهای اصلی
        self.create_sidebar(main_container)

        # Content Area
        self.content_area = tk.Frame(main_container, bg=self.colors['bg'])
        self.content_area.pack(side='left', fill='both', expand=True, padx=20, pady=20)

        # نمایش داشبورد اولیه
        self.show_dashboard()

        # Status Bar
        self.create_status_bar()

        # Update time
        self.update_time()

    def create_title_bar(self):
        """ایجاد Title Bar"""
        self.title_bar = tk.Frame(self.root, bg=self.colors['title_bar'], height=32)
        self.title_bar.pack(fill='x')
        self.title_bar.pack_propagate(False)

        # عنوان برنامه
        title_text = tk.Label(self.title_bar,
                              text="نرم افزار مدیریت کسب و کار",
                              bg=self.colors['title_bar'],
                              fg=self.colors['text_light'],
                              font=self.fonts['normal'])
        title_text.pack(side='left', padx=12)

        # کنترل‌های پنجره
        controls_frame = tk.Frame(self.title_bar, bg=self.colors['title_bar'])
        controls_frame.pack(side='right')

        # دکمه‌های کنترل
        control_buttons = [
            ("‎", "#5a5a5a", lambda: self.root.state('iconic')),  # کمینه
            ("‎", "#5a5a5a", self.toggle_maximize),  # بیشینه
            ("‎", "#c42b1c", self.root.quit)  # بستن
        ]

        for text, color, command in control_buttons:
            btn = tk.Label(controls_frame, text=text,
                           bg=self.colors['title_bar'],
                           fg='white',
                           font=("Segoe MDL2 Assets", 10),
                           padx=15,
                           cursor='hand2')
            btn.pack(side='left')

            # افکت hover
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['title_bar']))
            btn.bind("<Button-1>", lambda e, cmd=command: cmd())

    def create_sidebar(self, parent):
        """ایجاد نوار کناری با منوهای اصلی"""
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # لوگو یا عنوان سایدبار
        sidebar_header = tk.Label(sidebar,
                                  text="منوی اصلی",
                                  bg=self.colors['accent'],
                                  fg='white',
                                  font=self.fonts['subtitle'],
                                  pady=15)
        sidebar_header.pack(fill='x')

        # آیتم‌های منوی اصلی
        menu_items = [
            ("", "داشبورد", "dashboard", self.show_dashboard),
            ("", "ورودی جدید", "new_entry", self.show_new_entry),
            ("", "پایگاه داده", "database", self.show_database),
            ("", "گزارش گیری", "reports", self.show_reports),
            ("", "مدیریت کارکنان", "employees", self.show_employees),
            ("", "جستجو", "search", self.show_search),
            ("", "تنظیمات", "settings", self.show_settings),
            ("", "خروج", "exit", self.exit_app)
        ]

        for icon, text, page_id, command in menu_items:
            menu_btn = self.create_menu_button(sidebar, icon, text, page_id, command)
            menu_btn.pack(fill='x', padx=5, pady=2)

        # آمار سریع
        stats_frame = tk.Frame(sidebar, bg=self.colors['sidebar'], pady=20)
        stats_frame.pack(side='bottom', fill='x')

        stats = [
            ("", "تعداد رکوردها", "۱۲۵"),
            ("", "کارکنان", "۲۳"),
            ("", "گزارش‌ها", "۱۵"),
            ("", "امروز", "۸")
        ]

        for icon, text, value in stats:
            stat_widget = self.create_stat_widget(stats_frame, icon, text, value)
            stat_widget.pack(fill='x', padx=10, pady=3)

    def create_menu_button(self, parent, icon, text, page_id, command):
        """ایجاد دکمه منو"""
        btn_frame = tk.Frame(parent, bg=self.colors['sidebar'], cursor='hand2')

        # آیکون
        icon_label = tk.Label(btn_frame,
                              text=icon,
                              font=("Segoe MDL2 Assets", 16),
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_secondary'],
                              padx=15)
        icon_label.pack(side='left')

        # متن
        text_label = tk.Label(btn_frame,
                              text=text,
                              font=self.fonts['normal'],
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_primary'])
        text_label.pack(side='left', fill='x', expand=True, anchor='w')

        # نشانگر صفحه فعال
        self.indicator = tk.Label(btn_frame, text="", bg=self.colors['sidebar'], width=2)
        self.indicator.pack(side='right', padx=10)

        # افکت hover و کلیک
        def on_enter(e):
            if self.current_page != page_id:
                btn_frame.config(bg=self.colors['hover_bg'])
                icon_label.config(bg=self.colors['hover_bg'])
                text_label.config(bg=self.colors['hover_bg'])
                self.indicator.config(bg=self.colors['hover_bg'])

        def on_leave(e):
            if self.current_page != page_id:
                btn_frame.config(bg=self.colors['sidebar'])
                icon_label.config(bg=self.colors['sidebar'])
                text_label.config(bg=self.colors['sidebar'])
                self.indicator.config(bg=self.colors['sidebar'])

        def on_click(e):
            self.current_page = page_id
            self.highlight_active_menu()
            command()

        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)
        btn_frame.bind("<Button-1>", on_click)

        icon_label.bind("<Enter>", on_enter)
        icon_label.bind("<Leave>", on_leave)
        icon_label.bind("<Button-1>", on_click)

        text_label.bind("<Enter>", on_enter)
        text_label.bind("<Leave>", on_leave)
        text_label.bind("<Button-1>", on_click)

        # ذخیره ویجت‌ها برای تغییر رنگ بعداً
        btn_frame.widgets = (btn_frame, icon_label, text_label, self.indicator)
        btn_frame.page_id = page_id

        return btn_frame

    def highlight_active_menu(self):
        """هایلایت کردن منوی فعال"""
        for widget in self.content_area.winfo_children():
            if hasattr(widget, 'page_id'):
                if widget.page_id == self.current_page:
                    widget.config(bg=self.colors['accent'])
                    for w in widget.widgets:
                        w.config(bg=self.colors['accent'], fg='white')
                else:
                    widget.config(bg=self.colors['sidebar'])
                    for w in widget.widgets:
                        w.config(bg=self.colors['sidebar'])
                        if w == widget.widgets[2]:  # متن
                            w.config(fg=self.colors['text_primary'])
                        else:
                            w.config(fg=self.colors['text_secondary'])

    def create_stat_widget(self, parent, icon, text, value):
        """ایجاد ویجت آمار"""
        frame = tk.Frame(parent, bg=self.colors['sidebar'])

        # آیکون
        tk.Label(frame, text=icon, font=("Segoe MDL2 Assets", 12),
                 bg=self.colors['sidebar'], fg=self.colors['accent']).pack(side='left', padx=5)

        # متن و مقدار
        text_frame = tk.Frame(frame, bg=self.colors['sidebar'])
        text_frame.pack(side='left', fill='x', expand=True)

        tk.Label(text_frame, text=text, font=self.fonts['small'],
                 bg=self.colors['sidebar'], fg=self.colors['text_secondary']).pack(anchor='w')
        tk.Label(text_frame, text=value, font=self.fonts['subtitle'],
                 bg=self.colors['sidebar'], fg=self.colors['text_primary']).pack(anchor='w')

        return frame

    # ==================== صفحات اصلی ====================

    def clear_content_area(self):
        """پاک کردن محتوای فعلی"""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """نمایش داشبورد"""
        self.clear_content_area()

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="داشبورد مدیریت",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        tk.Label(header_frame, text=datetime.now().strftime("%Y/%m/%d"),
                 font=self.fonts['small'], bg=self.colors['bg'],
                 fg=self.colors['text_secondary']).pack(side='right')

        # کارت‌های آمار
        stats_cards = tk.Frame(self.content_area, bg=self.colors['bg'])
        stats_cards.pack(fill='x', pady=10)

        stats = [
            ("", "ورودی‌های امروز", "۸ مورد", "#0078d4", "ورود به بخش"),
            ("", "کل رکوردها", "۱۲۵ مورد", "#28a745", "مشاهده همه"),
            ("", "کارکنان فعال", "۱۸ نفر", "#ffc107", "مدیریت"),
            ("", "گزارش‌های ماه", "۷ گزارش", "#dc3545", "مشاهده")
        ]

        for i, (icon, title, value, color, action) in enumerate(stats):
            card = self.create_dashboard_card(stats_cards, icon, title, value, color, action)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            stats_cards.columnconfigure(i, weight=1)

        # فعالیت‌های اخیر
        recent_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        recent_frame.pack(fill='both', expand=True, pady=20)

        # عنوان بخش
        tk.Label(recent_frame, text="فعالیت‌های اخیر",
                 font=self.fonts['subtitle'], bg=self.colors['bg']).pack(anchor='w', pady=(0, 10))

        # لیست فعالیت‌ها
        activities = [
            ("ثبت ورودی جدید توسط احمدی", "۱۰ دقیقه پیش"),
            ("گزارش فروش ماهانه تولید شد", "۱ ساعت پیش"),
            ("کارمند جدید ثبت شد: مریم محمدی", "۲ ساعت پیش"),
            ("به‌روزرسانی پایگاه داده", "۳ ساعت پیش"),
            ("جستجوی پرونده‌های مالی", "۵ ساعت پیش")
        ]

        for activity, time in activities:
            activity_widget = self.create_activity_widget(recent_frame, activity, time)
            activity_widget.pack(fill='x', pady=5)

    def show_new_entry(self):
        """صفحه ورودی جدید"""
        self.clear_content_area()

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="ثبت ورودی جدید",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # فرم ثبت ورودی
        form_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                              highlightbackground=self.colors['card_border'],
                              highlightthickness=1, padx=20, pady=20)
        form_frame.pack(fill='x', pady=10)

        # فیلدهای فرم
        fields = [
            ("نوع ورودی", ["فروش", "خرید", "موجودی", "سایر"]),
            ("عنوان ورودی", "entry"),
            ("مبلغ (ریال)", "number"),
            ("تاریخ", "date"),
            ("توضیحات", "textarea"),
            ("ضمیمه", "file")
        ]

        self.entry_fields = {}
        row = 0

        for label, field_type in fields:
            tk.Label(form_frame, text=label + ":", font=self.fonts['normal'],
                     bg=self.colors['card_bg']).grid(row=row, column=0, sticky='w', pady=10, padx=5)

            if isinstance(field_type, list):  # Dropdown
                var = tk.StringVar()
                var.set(field_type[0])
                dropdown = ttk.Combobox(form_frame, textvariable=var,
                                        values=field_type, state='readonly',
                                        font=self.fonts['normal'])
                dropdown.grid(row=row, column=1, sticky='ew', pady=10, padx=5)
                self.entry_fields[label] = dropdown

            elif field_type == "entry":
                entry = tk.Entry(form_frame, font=self.fonts['normal'],
                                 bg=self.colors['input_bg'], bd=1, relief='solid')
                entry.grid(row=row, column=1, sticky='ew', pady=10, padx=5)
                self.entry_fields[label] = entry

            elif field_type == "number":
                entry = tk.Entry(form_frame, font=self.fonts['normal'],
                                 bg=self.colors['input_bg'], bd=1, relief='solid')
                entry.grid(row=row, column=1, sticky='ew', pady=10, padx=5)
                self.entry_fields[label] = entry

            elif field_type == "date":
                entry = tk.Entry(form_frame, font=self.fonts['normal'],
                                 bg=self.colors['input_bg'], bd=1, relief='solid')
                entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
                entry.grid(row=row, column=1, sticky='ew', pady=10, padx=5)
                self.entry_fields[label] = entry

            elif field_type == "textarea":
                textarea = scrolledtext.ScrolledText(form_frame, height=4,
                                                     font=self.fonts['normal'],
                                                     bg=self.colors['input_bg'],
                                                     bd=1, relief='solid')
                textarea.grid(row=row, column=1, sticky='ew', pady=10, padx=5)
                self.entry_fields[label] = textarea

            elif field_type == "file":
                file_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
                file_frame.grid(row=row, column=1, sticky='ew', pady=10, padx=5)

                entry = tk.Entry(file_frame, font=self.fonts['normal'],
                                 bg=self.colors['input_bg'], bd=1, relief='solid',
                                 width=30)
                entry.pack(side='left', fill='x', expand=True)

                btn = tk.Button(file_frame, text="انتخاب فایل",
                                bg=self.colors['button_secondary'],
                                fg='white', font=self.fonts['small'],
                                command=lambda e=entry: self.select_file(e))
                btn.pack(side='left', padx=5)
                self.entry_fields[label] = entry

            row += 1

        form_frame.columnconfigure(1, weight=1)

        # دکمه‌های عمل
        buttons_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        buttons_frame.pack(fill='x', pady=20)

        tk.Button(buttons_frame, text="ذخیره ورودی",
                  bg=self.colors['button_success'], fg='white',
                  font=self.fonts['normal'], padx=30, pady=10,
                  command=self.save_entry).pack(side='right', padx=5)

        tk.Button(buttons_frame, text="پاک کردن فرم",
                  bg=self.colors['button_secondary'], fg='white',
                  font=self.fonts['normal'], padx=30, pady=10,
                  command=self.clear_form).pack(side='right', padx=5)

        tk.Button(buttons_frame, text="انصراف",
                  bg=self.colors['button_danger'], fg='white',
                  font=self.fonts['normal'], padx=30, pady=10,
                  command=self.show_dashboard).pack(side='left', padx=5)

    def show_database(self):
        """صفحه پایگاه داده"""
        self.clear_content_area()

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="مدیریت پایگاه داده",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # دکمه‌های عملیاتی
        action_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        action_frame.pack(fill='x', pady=10)

        actions = [
            ("", "مشاهده همه داده‌ها", self.view_all_data),
            ("", "پشتیبان‌گیری", self.backup_database),
            ("", "بازیابی", self.restore_database),
            ("", "به‌روزرسانی", self.update_database),
            ("", "پاکسازی", self.clean_database)
        ]

        for icon, text, command in actions:
            btn = self.create_action_button(action_frame, icon, text, command)
            btn.pack(side='left', padx=5)

        # جدول داده‌ها
        table_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                               highlightbackground=self.colors['card_border'],
                               highlightthickness=1)
        table_frame.pack(fill='both', expand=True, pady=20)

        # ایجاد Treeview
        columns = ('id', 'type', 'title', 'amount', 'date', 'description')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        # تعریف ستون‌ها
        tree.heading('id', text='شناسه')
        tree.heading('type', text='نوع')
        tree.heading('title', text='عنوان')
        tree.heading('amount', text='مبلغ')
        tree.heading('date', text='تاریخ')
        tree.heading('description', text='توضیحات')

        tree.column('id', width=50)
        tree.column('type', width=80)
        tree.column('title', width=150)
        tree.column('amount', width=100)
        tree.column('date', width=100)
        tree.column('description', width=200)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # قرار دادن ویجت‌ها
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # اضافه کردن داده‌های نمونه
        sample_data = [
            (1, 'فروش', 'فروش محصول A', '1,500,000', '1402/10/15', 'فروش نقدی'),
            (2, 'خرید', 'خرید مواد اولیه', '2,300,000', '1402/10/14', 'از تامین کننده X'),
            (3, 'موجودی', 'موجودی انبار', '4,500,000', '1402/10/13', 'موجودی پایان ماه'),
            (4, 'فروش', 'فروش محصول B', '800,000', '1402/10/12', 'فروش اقساطی'),
            (5, 'سایر', 'هزینه تبلیغات', '600,000', '1402/10/11', 'تبلیغات اینستاگرام')
        ]

        for item in sample_data:
            tree.insert('', tk.END, values=item)

    def show_reports(self):
        """صفحه گزارش گیری"""
        self.clear_content_area()

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="گزارش‌گیری و آمار",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # انواع گزارش‌ها
        reports_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        reports_frame.pack(fill='x', pady=10)

        reports = [
            ("", "گزارش مالی ماهانه", "تحلیل درآمد و هزینه‌ها", self.generate_financial_report),
            ("📊", "گزارش فروش", "آمار فروش به تفکیک محصول", self.generate_sales_report),
            ("📈", "گزارش کارکنان", "عملکرد و حضور و غیاب", self.generate_employee_report),
            ("📉", "گزارش موجودی", "وضعیت انبار و کالاها", self.generate_inventory_report),
            ("📋", "گزارش سفارشی", "ساخت گزارش دلخواه", self.generate_custom_report)
        ]

        for i, (icon, title, desc, command) in enumerate(reports):
            card = self.create_report_card(reports_frame, icon, title, desc, command)
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky='nsew')
            reports_frame.columnconfigure(i % 3, weight=1)

        # فیلترهای گزارش
        filter_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                                highlightbackground=self.colors['card_border'],
                                highlightthickness=1, padx=15, pady=15)
        filter_frame.pack(fill='x', pady=20)

        tk.Label(filter_frame, text="فیلترهای پیشرفته:",
                 font=self.fonts['subtitle'], bg=self.colors['card_bg']).pack(anchor='w', pady=(0, 10))

        # فیلترها
        filters = tk.Frame(filter_frame, bg=self.colors['card_bg'])
        filters.pack(fill='x')

        tk.Label(filters, text="بازه زمانی:", font=self.fonts['normal'],
                 bg=self.colors['card_bg']).grid(row=0, column=0, sticky='w', padx=5, pady=5)

        date_frame = tk.Frame(filters, bg=self.colors['card_bg'])
        date_frame.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        tk.Entry(date_frame, width=12, font=self.fonts['normal']).pack(side='left', padx=2)
        tk.Label(date_frame, text="تا", bg=self.colors['card_bg']).pack(side='left', padx=2)
        tk.Entry(date_frame, width=12, font=self.fonts['normal']).pack(side='left', padx=2)

        tk.Button(filters, text="اعمال فیلترها", bg=self.colors['button_primary'],
                  fg='white', font=self.fonts['small']).grid(row=0, column=2, padx=20)

    def show_employees(self):
        """صفحه مدیریت کارکنان"""
        self.clear_content_area()

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="مدیریت کارکنان",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # دکمه‌های مدیریت
        management_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        management_frame.pack(fill='x', pady=10)

        actions = [
            ("", "افزودن کارمند", self.add_employee),
            ("", "ویرایش اطلاعات", self.edit_employee),
            ("", "حذف کارمند", self.delete_employee),
            ("", "لیست حقوق", self.salary_list),
            ("", "تنظیمات دسترسی", self.access_settings)
        ]

        for icon, text, command in actions:
            btn = self.create_action_button(management_frame, icon, text, command)
            btn.pack(side='left', padx=5)

        # جدول کارکنان
        table_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                               highlightbackground=self.colors['card_border'],
                               highlightthickness=1, padx=10, pady=10)
        table_frame.pack(fill='both', expand=True, pady=20)

        # ایجاد Treeview برای کارکنان
        columns = ('id', 'name', 'position', 'department', 'phone', 'status')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)

        # تعریف ستون‌ها
        tree.heading('id', text='کد پرسنلی')
        tree.heading('name', text='نام و نام خانوادگی')
        tree.heading('position', text='سمت')
        tree.heading('department', text='بخش')
        tree.heading('phone', text='تلفن')
        tree.heading('status', text='وضعیت')

        tree.column('id', width=80)
        tree.column('name', width=150)
        tree.column('position', width=100)
        tree.column('department', width=100)
        tree.column('phone', width=100)
        tree.column('status', width=80)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # داده‌های نمونه کارکنان
        employees = [
            (1001, 'علی احمدی', 'مدیر فروش', 'فروش', '09123456789', 'فعال'),
            (1002, 'مریم محمدی', 'حسابدار', 'مالی', '09129876543', 'فعال'),
            (1003, 'رضا کریمی', 'انباردار', 'انبار', '09131234567', 'فعال'),
            (1004, 'سارا حسینی', 'منشی', 'اداری', '09137654321', 'مرخصی'),
            (1005, 'امیر جعفری', 'برنامه نویس', 'فنی', '09149876543', 'فعال')
        ]

        for emp in employees:
            tree.insert('', tk.END, values=emp)

    def show_search(self):
        """صفحه جستجو"""
        self.clear_content_area()

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="جستجوی پیشرفته",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # کادر جستجو
        search_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                                highlightbackground=self.colors['card_border'],
                                highlightthickness=1, padx=20, pady=20)
        search_frame.pack(fill='x', pady=10)

        # فیلد جستجوی اصلی
        main_search_frame = tk.Frame(search_frame, bg=self.colors['card_bg'])
        main_search_frame.pack(fill='x', pady=(0, 15))

        tk.Label(main_search_frame, text="عبارت جستجو:",
                 font=self.fonts['normal'], bg=self.colors['card_bg']).pack(side='left', padx=5)

        search_entry = tk.Entry(main_search_frame, font=self.fonts['normal'],
                                width=50, bg=self.colors['input_bg'],
                                bd=1, relief='solid')
        search_entry.pack(side='left', fill='x', expand=True, padx=5)

        tk.Button(main_search_frame, text="جستجو",
                  bg=self.colors['button_primary'], fg='white',
                  font=self.fonts['normal'], padx=20,
                  command=lambda: self.perform_search(search_entry.get())).pack(side='left', padx=5)

        # فیلترهای جستجو
        tk.Label(search_frame, text="فیلترهای جستجو:",
                 font=self.fonts['subtitle'], bg=self.colors['card_bg']).pack(anchor='w', pady=(0, 10))

        filters_frame = tk.Frame(search_frame, bg=self.colors['card_bg'])
        filters_frame.pack(fill='x')

        # نوع جستجو
        tk.Label(filters_frame, text="نوع جستجو:",
                 font=self.fonts['normal'], bg=self.colors['card_bg']).grid(row=0, column=0, sticky='w', pady=5, padx=5)

        search_type = ttk.Combobox(filters_frame, values=['همه', 'کارکنان', 'ورودی‌ها', 'گزارش‌ها', 'اسناد'],
                                   state='readonly', font=self.fonts['normal'], width=15)
        search_type.set('همه')
        search_type.grid(row=0, column=1, sticky='w', pady=5, padx=5)

        # بازه زمانی
        tk.Label(filters_frame, text="بازه زمانی:",
                 font=self.fonts['normal'], bg=self.colors['card_bg']).grid(row=0, column=2, sticky='w', pady=5,
                                                                            padx=20)

        date_frame = tk.Frame(filters_frame, bg=self.colors['card_bg'])
        date_frame.grid(row=0, column=3, sticky='w', pady=5, padx=5)

        tk.Entry(date_frame, width=10, font=self.fonts['normal']).pack(side='left')
        tk.Label(date_frame, text="تا", bg=self.colors['card_bg']).pack(side='left', padx=2)
        tk.Entry(date_frame, width=10, font=self.fonts['normal']).pack(side='left')

        # نتایج جستجو
        results_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        results_frame.pack(fill='both', expand=True, pady=20)

        tk.Label(results_frame, text="نتایج جستجو:",
                 font=self.fonts['subtitle'], bg=self.colors['bg']).pack(anchor='w', pady=(0, 10))

        # لیست نتایج
        results_list = tk.Listbox(results_frame, font=self.fonts['normal'],
