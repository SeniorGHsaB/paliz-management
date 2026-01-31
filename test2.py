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
        indicator = tk.Label(btn_frame, text="", bg=self.colors['sidebar'], width=2)
        indicator.pack(side='right', padx=10)

        # افکت hover و کلیک
        def on_enter(e):
            if self.current_page != page_id:
                btn_frame.config(bg=self.colors['hover_bg'])
                icon_label.config(bg=self.colors['hover_bg'])
                text_label.config(bg=self.colors['hover_bg'])
                indicator.config(bg=self.colors['hover_bg'])

        def on_leave(e):
            if self.current_page != page_id:
                btn_frame.config(bg=self.colors['sidebar'])
                icon_label.config(bg=self.colors['sidebar'])
                text_label.config(bg=self.colors['sidebar'])
                indicator.config(bg=self.colors['sidebar'])

        def on_click(e):
            self.current_page = page_id
            self.highlight_active_menu(btn_frame)
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

        # ذخیره اطلاعات
        btn_frame.icon_label = icon_label
        btn_frame.text_label = text_label
        btn_frame.indicator = indicator
        btn_frame.page_id = page_id

        return btn_frame

    def highlight_active_menu(self, active_frame):
        """هایلایت کردن منوی فعال"""
        # ریست همه منوها
        for widget in self.content_area.master.winfo_children()[1].winfo_children():  # دسترسی به سایدبار
            if isinstance(widget, tk.Frame) and hasattr(widget, 'page_id'):
                if widget.page_id == self.current_page:
                    widget.config(bg=self.colors['accent'])
                    widget.icon_label.config(bg=self.colors['accent'], fg='white')
                    widget.text_label.config(bg=self.colors['accent'], fg='white')
                    widget.indicator.config(bg=self.colors['accent'])
                else:
                    widget.config(bg=self.colors['sidebar'])
                    widget.icon_label.config(bg=self.colors['sidebar'], fg=self.colors['text_secondary'])
                    widget.text_label.config(bg=self.colors['sidebar'], fg=self.colors['text_primary'])
                    widget.indicator.config(bg=self.colors['sidebar'])

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

    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = tk.Frame(self.root,
                                   bg=self.colors['title_bar_light'],
                                   height=24)
        self.status_bar.pack(fill='x')
        self.status_bar.pack_propagate(False)

        # سمت چپ - وضعیت
        left_frame = tk.Frame(self.status_bar, bg=self.colors['title_bar_light'])
        left_frame.pack(side='left', padx=10)

        self.status_label = tk.Label(left_frame,
                                     text="آماده",
                                     bg=self.colors['title_bar_light'],
                                     fg=self.colors['text_light'],
                                     font=self.fonts['small'])
        self.status_label.pack(side='left')

        # سمت راست - اطلاعات
        right_frame = tk.Frame(self.status_bar, bg=self.colors['title_bar_light'])
        right_frame.pack(side='right', padx=10)

        self.time_label = tk.Label(right_frame,
                                   text="",
                                   bg=self.colors['title_bar_light'],
                                   fg=self.colors['text_light'],
                                   font=self.fonts['small'])
        self.time_label.pack(side='right', padx=10)

        # آیکون‌های سیستم
        system_icons = ["", "", "", ""]
        for icon in system_icons:
            tk.Label(right_frame,
                     text=icon,
                     bg=self.colors['title_bar_light'],
                     fg=self.colors['text_light'],
                     font=("Segoe MDL2 Assets", 10),
                     padx=5,
                     cursor='hand2').pack(side='right')

    def update_time(self):
        """به‌روزرسانی زمان"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

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
            self.create_activity_widget(recent_frame, activity, time)

    def create_dashboard_card(self, parent, icon, title, value, color, action_text):
        """ایجاد کارت داشبورد"""
        card = tk.Frame(parent, bg=self.colors['card_bg'],
                        highlightbackground=self.colors['card_border'],
                        highlightthickness=1)

        # محتوا
        content_frame = tk.Frame(card, bg=self.colors['card_bg'], padx=15, pady=15)
        content_frame.pack(fill='both', expand=True)

        # آیکون و عنوان
        icon_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        icon_frame.pack(fill='x', pady=(0, 10))

        tk.Label(icon_frame, text=icon, font=("Segoe MDL2 Assets", 20),
                 bg=self.colors['card_bg'], fg=color).pack(side='left')

        tk.Label(icon_frame, text=title, font=self.fonts['normal'],
                 bg=self.colors['card_bg']).pack(side='left', padx=10)

        # مقدار
        tk.Label(content_frame, text=value, font=self.fonts['large'],
                 bg=self.colors['card_bg'], fg=color).pack(anchor='w', pady=(0, 10))

        # دکمه عمل
        tk.Button(content_frame, text=action_text,
                  bg=color, fg='white',
                  font=self.fonts['small'], padx=15, pady=5,
                  cursor='hand2').pack(anchor='w')

        return card

    def create_activity_widget(self, parent, activity, time):
        """ایجاد ویجت فعالیت"""
        frame = tk.Frame(parent, bg=self.colors['card_bg'],
                         highlightbackground=self.colors['card_border'],
                         highlightthickness=1)
        frame.pack(fill='x', pady=5)

        # نقطه
        tk.Label(frame, text="●", font=self.fonts['normal'],
                 bg=self.colors['card_bg'], fg=self.colors['accent']).pack(side='left', padx=10)

        # متن فعالیت
        tk.Label(frame, text=activity, font=self.fonts['normal'],
                 bg=self.colors['card_bg']).pack(side='left', fill='x', expand=True, anchor='w')

        # زمان
        tk.Label(frame, text=time, font=self.fonts['small'],
                 bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(side='right', padx=10)

    def show_new_entry(self):
        """صفحه ورودی جدید"""
        self.clear_content_area()
        self.status_label.config(text="صفحه ثبت ورودی جدید")

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
            ("توضیحات", "textarea")
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

    def save_entry(self):
        """ذخیره ورودی جدید"""
        try:
            entry_data = {}
            for label, field in self.entry_fields.items():
                if isinstance(field, ttk.Combobox):
                    entry_data[label] = field.get()
                elif isinstance(field, scrolledtext.ScrolledText):
                    entry_data[label] = field.get("1.0", tk.END).strip()
                else:
                    entry_data[label] = field.get()

            # اعتبارسنجی
            if not entry_data.get('عنوان ورودی'):
                messagebox.showwarning("اخطار", "لطفا عنوان ورودی را وارد کنید")
                return

            # نمایش پیام موفقیت
            messagebox.showinfo("موفقیت", "ورودی جدید با موفقیت ثبت شد")
            self.show_dashboard()

        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ثبت ورودی: {str(e)}")

    def clear_form(self):
        """پاک کردن فرم"""
        for label, field in self.entry_fields.items():
            if isinstance(field, ttk.Combobox):
                if field['values']:
                    field.set(field['values'][0])
            elif isinstance(field, scrolledtext.ScrolledText):
                field.delete("1.0", tk.END)
            else:
                field.delete(0, tk.END)

    def show_database(self):
        """صفحه پایگاه داده"""
        self.clear_content_area()
        self.status_label.config(text="مدیریت پایگاه داده")

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="مدیریت پایگاه داده",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # دکمه‌های عملیاتی
        action_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        action_frame.pack(fill='x', pady=10)

        actions = [
            ("", "مشاهده همه", self.view_all_data),
            ("", "پشتیبان‌گیری", self.backup_database),
            ("", "بازیابی", self.restore_database),
            ("", "ویرایش", self.edit_database),
            ("", "پاکسازی", self.clean_database)
        ]

        for icon, text, command in actions:
            self.create_action_button(action_frame, icon, text, command)

        # جدول داده‌ها
        table_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                               highlightbackground=self.colors['card_border'],
                               highlightthickness=1)
        table_frame.pack(fill='both', expand=True, pady=20)

        # ایجاد Treeview
        columns = ('id', 'type', 'title', 'amount', 'date')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        # تعریف ستون‌ها
        tree.heading('id', text='شناسه')
        tree.heading('type', text='نوع')
        tree.heading('title', text='عنوان')
        tree.heading('amount', text='مبلغ')
        tree.heading('date', text='تاریخ')

        tree.column('id', width=50)
        tree.column('type', width=80)
        tree.column('title', width=150)
        tree.column('amount', width=100)
        tree.column('date', width=100)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # داده‌های نمونه
        sample_data = [
            (1, 'فروش', 'فروش محصول A', '1,500,000', '1402/10/15'),
            (2, 'خرید', 'خرید مواد اولیه', '2,300,000', '1402/10/14'),
            (3, 'موجودی', 'موجودی انبار', '4,500,000', '1402/10/13'),
            (4, 'فروش', 'فروش محصول B', '800,000', '1402/10/12'),
            (5, 'سایر', 'هزینه تبلیغات', '600,000', '1402/10/11')
        ]

        for item in sample_data:
            tree.insert('', tk.END, values=item)

    def show_reports(self):
        """صفحه گزارش گیری"""
        self.clear_content_area()
        self.status_label.config(text="گزارش‌گیری و آمار")

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="گزارش‌گیری و آمار",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # انواع گزارش‌ها
        reports_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        reports_frame.pack(fill='x', pady=10)

        reports = [
            ("", "گزارش مالی", "تحلیل درآمد و هزینه‌ها", self.generate_financial_report),
            ("📊", "گزارش فروش", "آمار فروش محصولات", self.generate_sales_report),
            ("📈", "کارکنان", "عملکرد و حضور و غیاب", self.generate_employee_report),
            ("📉", "موجودی", "وضعیت انبار", self.generate_inventory_report)
        ]

        for i, (icon, title, desc, command) in enumerate(reports):
            self.create_report_card(reports_frame, icon, title, desc, command, i)

    def show_employees(self):
        """صفحه مدیریت کارکنان"""
        self.clear_content_area()
        self.status_label.config(text="مدیریت کارکنان")

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="مدیریت کارکنان",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # دکمه‌های مدیریت
        management_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        management_frame.pack(fill='x', pady=10)

        actions = [
            ("", "افزودن", self.add_employee),
            ("", "ویرایش", self.edit_employee),
            ("", "حذف", self.delete_employee),
            ("", "حقوق", self.salary_list)
        ]

        for icon, text, command in actions:
            self.create_action_button(management_frame, icon, text, command)

        # جدول کارکنان
        self.create_employee_table()

    def show_search(self):
        """صفحه جستجو"""
        self.clear_content_area()
        self.status_label.config(text="جستجوی پیشرفته")

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

        # فیلد جستجو
        search_entry = tk.Entry(search_frame, font=self.fonts['normal'],
                                width=50, bg=self.colors['input_bg'])
        search_entry.pack(side='left', fill='x', expand=True, padx=5)

        tk.Button(search_frame, text="جستجو",
                  bg=self.colors['button_primary'], fg='white',
                  font=self.fonts['normal'], padx=20,
                  command=lambda: self.perform_search(search_entry.get())).pack(side='left', padx=5)

    def show_settings(self):
        """صفحه تنظیمات"""
        self.clear_content_area()
        self.status_label.config(text="تنظیمات سیستم")

        # هدر
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        tk.Label(header_frame, text="تنظیمات سیستم",
                 font=self.fonts['title'], bg=self.colors['bg']).pack(side='left')

        # تنظیمات
        settings_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                                  highlightbackground=self.colors['card_border'],
                                  highlightthickness=1, padx=20, pady=20)
        settings_frame.pack(fill='x', pady=10)

        settings = [
            ("تم برنامه:", ["روشن", "تیره"]),
            ("زبان:", ["فارسی", "English"]),
            ("فرمت تاریخ:", ["۱۴۰۲/۱۰/۱۵", "2023/12/06"]),
            ("ذخیره‌سازی خودکار:", ["فعال", "غیرفعال"])
        ]

        for i, (label, options) in enumerate(settings):
            tk.Label(settings_frame, text=label, font=self.fonts['normal'],
                     bg=self.colors['card_bg']).grid(row=i, column=0, sticky='w', pady=10, padx=5)

            var = tk.StringVar()
            var.set(options[0])
            ttk.Combobox(settings_frame, textvariable=var,
                         values=options, state='readonly',
                         font=self.fonts['normal']).grid(row=i, column=1, sticky='w', pady=10, padx=5)

    # ==================== متدهای کمکی ====================

    def create_action_button(self, parent, icon, text, command):
        """ایجاد دکمه عمل"""
        btn = tk.Button(parent,
                        text=f"{icon} {text}",
                        bg=self.colors['button_primary'],
                        fg='white',
                        font=self.fonts['normal'],
                        padx=15,
                        pady=8,
                        cursor='hand2',
                        command=command)
        btn.pack(side='left', padx=5)
        return btn

    def create_report_card(self, parent, icon, title, desc, command, index):
        """ایجاد کارت گزارش"""
        card = tk.Frame(parent, bg=self.colors['card_bg'],
                        highlightbackground=self.colors['card_border'],
                        highlightthickness=1, width=200, height=150)
        card.grid(row=index // 3, column=index % 3, padx=10, pady=10, sticky='nsew')

        content = tk.Frame(card, bg=self.colors['card_bg'], padx=15, pady=15)
        content.pack(fill='both', expand=True)

        tk.Label(content, text=icon, font=("Segoe UI", 24),
                 bg=self.colors['card_bg']).pack(pady=(0, 10))

        tk.Label(content, text=title, font=self.fonts['subtitle'],
                 bg=self.colors['card_bg']).pack(pady=(0, 5))

        tk.Label(content, text=desc, font=self.fonts['small'],
                 bg=self.colors['card_bg'], fg=self.colors['text_secondary']).pack(pady=(0, 10))

        tk.Button(content, text="ایجاد گزارش",
                  bg=self.colors['button_primary'], fg='white',
                  font=self.fonts['small'], command=command).pack()

        return card

    def create_employee_table(self):
        """ایجاد جدول کارکنان"""
        table_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'],
                               highlightbackground=self.colors['card_border'],
                               highlightthickness=1, padx=10, pady=10)
        table_frame.pack(fill='both', expand=True, pady=20)

        # ایجاد Treeview
        columns = ('id', 'name', 'position', 'phone', 'status')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)

        # تعریف ستون‌ها
        tree.heading('id', text='کد پرسنلی')
        tree.heading('name', text='نام و نام خانوادگی')
        tree.heading('position', text='سمت')
        tree.heading('phone', text='تلفن')
        tree.heading('status', text='وضعیت')

        tree.column('id', width=80)
        tree.column('name', width=150)
        tree.column('position', width=100)
        tree.column('phone', width=100)
        tree.column('status', width=80)

        # نوار اسکرول
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # داده‌های نمونه
        employees = [
            (1001, 'علی احمدی', 'مدیر فروش', '09123456789', 'فعال'),
            (1002, 'مریم محمدی', 'حسابدار', '09129876543', 'فعال'),
            (1003, 'رضا کریمی', 'انباردار', '09131234567', 'فعال'),
            (1004, 'سارا حسینی', 'منشی', '09137654321', 'مرخصی'),
            (1005, 'امیر جعفری', 'برنامه نویس', '09149876543', 'فعال')
        ]

        for emp in employees:
            tree.insert('', tk.END, values=emp)

    # ==================== متدهای عملیاتی ====================

    def toggle_maximize(self):
        """تغییر حالت فول اسکرین"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

    def exit_app(self):
        """خروج از برنامه"""
        if messagebox.askyesno("خروج", "آیا از برنامه خارج می‌شوید؟"):
            self.root.quit()

    def create_sample_database(self):
        """ایجاد دیتابیس نمونه"""
        try:
            self.db_connection = sqlite3.connect(':memory:')
            cursor = self.db_connection.cursor()

            # ایجاد جدول ورودی‌ها
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS entries
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY,
                               type
                               TEXT,
                               title
                               TEXT,
                               amount
                               REAL,
                               date
                               TEXT,
                               description
                               TEXT
                           )
                           ''')

            # ایجاد جدول کارکنان
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS employees
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY,
                               name
                               TEXT,
                               position
                               TEXT,
                               department
                               TEXT,
                               phone
                               TEXT,
                               status
                               TEXT
                           )
                           ''')

            self.db_connection.commit()

        except Exception as e:
            print(f"خطا در ایجاد دیتابیس: {e}")

    def view_all_data(self):
        """مشاهده همه داده‌ها"""
        messagebox.showinfo("اطلاعات", "نمایش همه داده‌ها")

    def backup_database(self):
        """پشتیبان‌گیری از دیتابیس"""
        messagebox.showinfo("پشتیبان‌گیری", "پشتیبان‌گیری انجام شد")

    def restore_database(self):
        """بازیابی دیتابیس"""
        messagebox.showinfo("بازیابی", "بازیابی انجام شد")

    def edit_database(self):
        """ویرایش دیتابیس"""
        messagebox.showinfo("ویرایش", "ویرایش دیتابیس")

    def clean_database(self):
        """پاکسازی دیتابیس"""
        if messagebox.askyesno("پاکسازی", "آیا از پاکسازی دیتابیس مطمئن هستید؟"):
            messagebox.showinfo("پاکسازی", "دیتابیس پاکسازی شد")

    def generate_financial_report(self):
        """تولید گزارش مالی"""
        messagebox.showinfo("گزارش مالی", "گزارش مالی تولید شد")

    def generate_sales_report(self):
        """تولید گزارش فروش"""
        messagebox.showinfo("گزارش فروش", "گزارش فروش تولید شد")

    def generate_employee_report(self):
        """تولید گزارش کارکنان"""
        messagebox.showinfo("گزارش کارکنان", "گزارش کارکنان تولید شد")

    def generate_inventory_report(self):
        """تولید گزارش موجودی"""
        messagebox.showinfo("گزارش موجودی", "گزارش موجودی تولید شد")

    def add_employee(self):
        """افزودن کارمند جدید"""
        messagebox.showinfo("افزودن کارمند", "فرم افزودن کارمند جدید")

    def edit_employee(self):
        """ویرایش اطلاعات کارمند"""
        messagebox.showinfo("ویرایش کارمند", "ویرایش اطلاعات کارمند")

    def delete_employee(self):
        """حذف کارمند"""
        if messagebox.askyesno("حذف کارمند", "آیا از حذف کارمند مطمئن هستید؟"):
            messagebox.showinfo("حذف", "کارمند حذف شد")

    def salary_list(self):
        """لیست حقوق و دستمزد"""
        messagebox.showinfo("لیست حقوق", "نمایش لیست حقوق")

    def perform_search(self, query):
        """انجام جستجو"""
        if query:
            messagebox.showinfo("جستجو", f"نتایج جستجو برای: {query}")
        else:
            messagebox.showwarning("هشدار", "لطفا عبارت جستجو را وارد کنید")

    def bind_events(self):
        """اتصال رویدادها"""
        # کلیدهای میانبر
        self.root.bind('<F11>', lambda e: self.toggle_maximize())
        self.root.bind('<Escape>', lambda e: self.toggle_maximize())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        self.root.bind('<Alt-F4>', lambda e: self.exit_app())

        # میانبرهای صفحه‌ها
        self.root.bind('<F1>', lambda e: self.show_dashboard())
        self.root.bind('<F2>', lambda e: self.show_new_entry())
        self.root.bind('<F3>', lambda e: self.show_database())
        self.root.bind('<F4>', lambda e: self.show_reports())
        self.root.bind('<F5>', lambda e: self.show_employees())
        self.root.bind('<F6>', lambda e: self.show_search())

    def run(self):
        """اجرای برنامه"""
        # مرکز کردن پنجره
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.root.mainloop()


# اجرای برنامه
if __name__ == "__main__":
    app = BusinessManagementApp()
    app.run()
