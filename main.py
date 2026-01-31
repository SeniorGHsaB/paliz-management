import tkinter as tk
from tkinter import font
import ctypes
from datetime import datetime

# تنظیم DPI برای ویندوز
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class SimplePanelApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("پنل مدیریت ساده")

        # تنظیم فول اسکرین
        self.is_fullscreen = True
        self.root.attributes('-fullscreen', True)

        # رنگ‌های ویندوز 11
        self.colors = {
            'bg': '#f3f3f3',
            'sidebar': '#2d2d2d',
            'sidebar_hover': '#3d3d3d',
            'sidebar_active': '#0078d4',
            'content_bg': '#ffffff',
            'text_light': '#ffffff',
            'text_dark': '#000000',
            'text_gray': '#6c757d',
            'border': '#e0e0e0'
        }

        self.setup_fonts()
        self.setup_ui()
        self.bind_events()

    def setup_fonts(self):
        """تنظیم فونت‌ها"""
        self.fonts = {
            'title': font.Font(family="Segoe UI", size=16, weight="bold"),
            'sidebar': font.Font(family="Segoe UI", size=12),
            'content': font.Font(family="Segoe UI", size=11),
            'small': font.Font(family="Segoe UI", size=9)
        }

    def setup_ui(self):
        """ایجاد رابط کاربری"""
        # پنل سمت چپ
        self.create_sidebar()

        # ناحیه محتوا
        self.create_content_area()

        # نمایش صفحه اصلی اولیه
        self.show_home_page()

    def create_sidebar(self):
        """ایجاد پنل سمت چپ"""
        self.sidebar = tk.Frame(self.root, bg=self.colors['sidebar'], width=220)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # عنوان پنل
        title_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar_active'], height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="پنل مدیریت",
                 bg=self.colors['sidebar_active'],
                 fg=self.colors['text_light'],
                 font=self.fonts['title']).pack(expand=True)

        # آیتم‌های منو
        menu_items = [
            ("🏠", "صفحه اصلی", "home"),
            ("📝", "ورود اطلاعات", "data_entry"),
            ("📅", "برنامه ریزی", "planning"),
            ("⚙️", "تنظیمات", "settings"),
            ("🚪", "خروج", "exit")
        ]

        self.menu_buttons = []

        for icon, text, page_id in menu_items:
            btn = self.create_menu_button(self.sidebar, icon, text, page_id)
            btn.pack(fill='x', pady=1)
            self.menu_buttons.append(btn)

        # فاصله‌دهنده
        tk.Frame(self.sidebar, bg=self.colors['sidebar'], height=20).pack(fill='x')

        # اطلاعات کاربر (پایین پنل)
        user_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'], pady=10)
        user_frame.pack(side='bottom', fill='x')

        # نام کاربر
        tk.Label(user_frame, text="کاربر: مدیر سیستم",
                 bg=self.colors['sidebar'],
                 fg=self.colors['text_light'],
                 font=self.fonts['small']).pack(pady=(0, 5))

        # تاریخ و ساعت
        self.sidebar_time = tk.Label(user_frame, text="",
                                     bg=self.colors['sidebar'],
                                     fg=self.colors['text_light'],
                                     font=self.fonts['small'])
        self.sidebar_time.pack()
        self.update_sidebar_time()

    def create_menu_button(self, parent, icon, text, page_id):
        """ایجاد دکمه منو"""
        btn_frame = tk.Frame(parent, bg=self.colors['sidebar'], cursor='hand2', height=50)
        btn_frame.pack_propagate(False)

        # آیکون
        icon_label = tk.Label(btn_frame,
                              text=icon,
                              font=self.fonts['sidebar'],
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_light'],
                              padx=20)
        icon_label.pack(side='left')

        # متن
        text_label = tk.Label(btn_frame,
                              text=text,
                              font=self.fonts['sidebar'],
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_light'])
        text_label.pack(side='left', fill='x', expand=True, anchor='w')

        # نشانگر فعال
        indicator = tk.Frame(btn_frame, bg=self.colors['sidebar'], width=4)
        indicator.pack(side='right', fill='y')

        # ذخیره اطلاعات برای دسترسی بعدی
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

    def create_content_area(self):
        """ایجاد ناحیه محتوا"""
        # هدر
        self.header = tk.Frame(self.root, bg=self.colors['content_bg'], height=60)
        self.header.pack(fill='x')
        self.header.pack_propagate(False)

        # عنوان صفحه
        self.page_title = tk.Label(self.header,
                                   text="صفحه اصلی",
                                   bg=self.colors['content_bg'],
                                   fg=self.colors['text_dark'],
                                   font=self.fonts['title'])
        self.page_title.pack(side='left', padx=20)

        # دکمه کنترل پنجره
        controls_frame = tk.Frame(self.header, bg=self.colors['content_bg'])
        controls_frame.pack(side='right', padx=10)

        # دکمه کمینه
        min_btn = tk.Label(controls_frame, text="─",
                           bg=self.colors['content_bg'],
                           fg=self.colors['text_dark'],
                           font=("Arial", 14),
                           padx=10,
                           cursor='hand2')
        min_btn.pack(side='left')
        min_btn.bind("<Button-1>", lambda e: self.root.state('iconic'))

        # دکمه فول اسکرین/بازگشت
        self.fullscreen_btn = tk.Label(controls_frame, text="□",
                                       bg=self.colors['content_bg'],
                                       fg=self.colors['text_dark'],
                                       font=("Arial", 14),
                                       padx=10,
                                       cursor='hand2')
        self.fullscreen_btn.pack(side='left')
        self.fullscreen_btn.bind("<Button-1>", lambda e: self.toggle_fullscreen())

        # دکمه بستن
        close_btn = tk.Label(controls_frame, text="✕",
                             bg=self.colors['content_bg'],
                             fg=self.colors['text_dark'],
                             font=("Arial", 14),
                             padx=10,
                             cursor='hand2')
        close_btn.pack(side='left')
        close_btn.bind("<Button-1>", lambda e: self.exit_app())

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

        if page_id == "home":
            self.show_home_page()
            self.page_title.config(text="صفحه اصلی")
        elif page_id == "data_entry":
            self.show_data_entry_page()
            self.page_title.config(text="ورود اطلاعات")
        elif page_id == "planning":
            self.show_planning_page()
            self.page_title.config(text="برنامه ریزی")
        elif page_id == "settings":
            self.show_settings_page()
            self.page_title.config(text="تنظیمات")
        elif page_id == "exit":
            self.exit_app()

    def show_home_page(self):
        """نمایش صفحه اصلی"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=40, pady=40)
        container.pack(fill='both', expand=True)

        # متن خوشامدگویی
        welcome_frame = tk.Frame(container, bg=self.colors['content_bg'])
        welcome_frame.pack(expand=True)

        tk.Label(welcome_frame, text="👋",
                 font=("Segoe UI Emoji", 48),
                 bg=self.colors['content_bg']).pack(pady=(0, 20))

        tk.Label(welcome_frame, text="به پنل مدیریت خوش آمدید",
                 font=self.fonts['title'],
                 bg=self.colors['content_bg']).pack(pady=(0, 10))

        tk.Label(welcome_frame, text="از منوی سمت چپ برای دسترسی به بخش‌های مختلف استفاده کنید",
                 font=self.fonts['content'],
                 bg=self.colors['content_bg'],
                 fg=self.colors['text_gray']).pack()

        # کارت‌های اطلاعات
        cards_frame = tk.Frame(container, bg=self.colors['content_bg'])
        cards_frame.pack(fill='x', pady=(40, 0))

        cards = [
            ("📊", "آمار امروز", "15 ورودی جدید"),
            ("📈", "پروژه‌های فعال", "3 پروژه در حال اجرا"),
            ("👥", "کاربران", "8 کاربر آنلاین"),
            ("🕐", "زمان کار", "6 ساعت 24 دقیقه")
        ]

        for i, (icon, title, value) in enumerate(cards):
            card = self.create_info_card(cards_frame, icon, title, value)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            cards_frame.columnconfigure(i, weight=1)

    def show_data_entry_page(self):
        """صفحه ورود اطلاعات"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # عنوان بخش
        tk.Label(container, text="فرم ورود اطلاعات",
                 font=self.fonts['title'],
                 bg=self.colors['content_bg']).pack(anchor='w', pady=(0, 20))

        # فرم ساده
        form_frame = tk.Frame(container, bg=self.colors['content_bg'])
        form_frame.pack(fill='x')

        fields = [
            ("نام:", tk.Entry(form_frame, font=self.fonts['content'], width=40)),
            ("موضوع:", tk.Entry(form_frame, font=self.fonts['content'], width=40)),
            ("توضیحات:", tk.Text(form_frame, font=self.fonts['content'], width=40, height=5))
        ]

        for i, (label, widget) in enumerate(fields):
            tk.Label(form_frame, text=label,
                     font=self.fonts['content'],
                     bg=self.colors['content_bg']).grid(row=i, column=0, sticky='w', pady=10, padx=5)

            widget.grid(row=i, column=1, sticky='w', pady=10, padx=5)

        # دکمه‌ها
        buttons_frame = tk.Frame(container, bg=self.colors['content_bg'])
        buttons_frame.pack(fill='x', pady=30)

        tk.Button(buttons_frame, text="ذخیره اطلاعات",
                  bg=self.colors['sidebar_active'],
                  fg='white',
                  font=self.fonts['content'],
                  padx=20,
                  pady=10).pack(side='right', padx=5)

        tk.Button(buttons_frame, text="پاک کردن",
                  bg=self.colors['text_gray'],
                  fg='white',
                  font=self.fonts['content'],
                  padx=20,
                  pady=10).pack(side='right', padx=5)

    def show_planning_page(self):
        """صفحه برنامه ریزی"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # عنوان بخش
        tk.Label(container, text="برنامه‌ریزی و زمان‌بندی",
                 font=self.fonts['title'],
                 bg=self.colors['content_bg']).pack(anchor='w', pady=(0, 20))

        # تقویم ساده
        calendar_frame = tk.Frame(container, bg=self.colors['content_bg'])
        calendar_frame.pack(fill='x', pady=10)

        # روزهای هفته
        days = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
        for i, day in enumerate(days):
            tk.Label(calendar_frame, text=day,
                     bg=self.colors['sidebar_active'],
                     fg='white',
                     font=self.fonts['content'],
                     padx=10,
                     pady=5).grid(row=0, column=i, padx=1, pady=1)

        # روزهای ماه (نمونه)
        day_num = 1
        for row in range(1, 6):
            for col in range(7):
                if day_num <= 31:
                    tk.Label(calendar_frame, text=str(day_num),
                             bg='white',
                             fg=self.colors['text_dark'],
                             font=self.fonts['content'],
                             borderwidth=1,
                             relief='solid',
                             width=4,
                             height=2).grid(row=row, column=col, padx=1, pady=1)
                    day_num += 1

        # لیست کارها
        tk.Label(container, text="لیست کارهای امروز",
                 font=self.fonts['title'],
                 bg=self.colors['content_bg']).pack(anchor='w', pady=(30, 10))

        tasks_frame = tk.Frame(container, bg=self.colors['content_bg'])
        tasks_frame.pack(fill='both', expand=True)

        tasks = [
            "✅ جلسه تیم برنامه‌نویسی (10:00)",
            "⏳ تکمیل گزارش ماهانه",
            "📞 تماس با مشتری جدید",
            "📧 پاسخ به ایمیل‌ها",
            "📊 بررسی آمار فروش"
        ]

        for task in tasks:
            tk.Label(tasks_frame, text=task,
                     bg=self.colors['content_bg'],
                     font=self.fonts['content'],
                     anchor='w',
                     pady=5).pack(fill='x')

    def show_settings_page(self):
        """صفحه تنظیمات"""
        container = tk.Frame(self.content_frame, bg=self.colors['content_bg'], padx=30, pady=30)
        container.pack(fill='both', expand=True)

        # عنوان بخش
        tk.Label(container, text="تنظیمات سیستم",
                 font=self.fonts['title'],
                 bg=self.colors['content_bg']).pack(anchor='w', pady=(0, 20))

        # تنظیمات
        settings_frame = tk.Frame(container, bg=self.colors['content_bg'])
        settings_frame.pack(fill='x')

        settings = [
            ("نمایش:", "روشن", ["روشن", "تیره"]),
            ("زبان:", "فارسی", ["فارسی", "انگلیسی"]),
            ("ذخیره‌سازی خودکار:", "فعال", ["فعال", "غیرفعال"]),
            ("نوتیفیکیشن:", "فعال", ["فعال", "غیرفعال"])
        ]

        for i, (label, default, options) in enumerate(settings):
            tk.Label(settings_frame, text=label,
                     font=self.fonts['content'],
                     bg=self.colors['content_bg']).grid(row=i, column=0, sticky='w', pady=10, padx=5)

            var = tk.StringVar(value=default)
            tk.OptionMenu(settings_frame, var, *options).grid(row=i, column=1, sticky='w', pady=10, padx=5)

    def create_info_card(self, parent, icon, title, value):
        """ایجاد کارت اطلاعات"""
        card = tk.Frame(parent, bg='white',
                        highlightbackground=self.colors['border'],
                        highlightthickness=1)

        content = tk.Frame(card, bg='white', padx=15, pady=15)
        content.pack(fill='both', expand=True)

        # آیکون
        tk.Label(content, text=icon,
                 font=("Segoe UI Emoji", 24),
                 bg='white').pack(anchor='w', pady=(0, 10))

        # عنوان
        tk.Label(content, text=title,
                 font=self.fonts['content'],
                 bg='white',
                 fg=self.colors['text_gray']).pack(anchor='w', pady=(0, 5))

        # مقدار
        tk.Label(content, text=value,
                 font=self.fonts['title'],
                 bg='white',
                 fg=self.colors['sidebar_active']).pack(anchor='w')

        return card

    def update_sidebar_time(self):
        """به‌روزرسانی زمان در پنل"""
        current_time = datetime.now().strftime("%H:%M - %Y/%m/%d")
        self.sidebar_time.config(text=current_time)
        self.root.after(1000, self.update_sidebar_time)

    def toggle_fullscreen(self):
        """تغییر حالت فول اسکرین"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

        # تغییر آیکون دکمه
        if self.is_fullscreen:
            self.fullscreen_btn.config(text="❐")
        else:
            self.fullscreen_btn.config(text="□")

    def exit_app(self):
        """خروج از برنامه"""
        self.root.quit()

    def bind_events(self):
        """اتصال رویدادها"""
        # کلیدهای میانبر
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Alt-F4>', lambda e: self.exit_app())

    def run(self):
        """اجرای برنامه"""
        # تنظیم اندازه اولیه
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.mainloop()


# اجرای برنامه
if __name__ == "__main__":
    app = SimplePanelApp()
    app.run()