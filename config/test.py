import tkinter as tk
from tkinter import ttk, font
import ctypes
from datetime import datetime

# تنظیم DPI برای ویندوز
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


class WindowsStyleApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Windows Style Application - برنامه با استایل ویندوز")

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
            'card_bg': '#ffffff',
            'card_border': '#e0e0e0',
            'text_primary': '#000000',
            'text_secondary': '#6c757d',
            'text_light': '#ffffff',
            'accent': '#0078d4',
            'hover_bg': '#f5f5f5'
        }

        self.setup_fonts()
        self.setup_ui()
        self.bind_events()

    def setup_fonts(self):
        """تنظیم فونت‌های ویندوز مانند"""
        self.fonts = {
            'title': font.Font(family="Segoe UI", size=16, weight="bold"),
            'subtitle': font.Font(family="Segoe UI", size=12, weight="bold"),
            'normal': font.Font(family="Segoe UI", size=11),
            'small': font.Font(family="Segoe UI", size=9),
            'large': font.Font(family="Segoe UI", size=14),
            'icon': font.Font(family="Segoe MDL2 Assets", size=12)
        }

    def setup_ui(self):
        """ایجاد رابط کاربری"""
        # Title Bar
        self.create_title_bar()

        # Toolbar
        self.create_toolbar()

        # Main Container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True)

        # Sidebar
        self.create_sidebar(main_container)

        # Content Area
        self.create_content_area(main_container)

        # Status Bar
        self.create_status_bar()

        # Update time
        self.update_time()

    def create_title_bar(self):
        """ایجاد Title Bar شبیه ویندوز"""
        self.title_bar = tk.Frame(self.root, bg=self.colors['title_bar'], height=32)
        self.title_bar.pack(fill='x')
        self.title_bar.pack_propagate(False)

        # عنوان برنامه
        title_text = tk.Label(self.title_bar,
                              text="برنامه با استایل ویندوز",
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

    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        toolbar = tk.Frame(self.root, bg='white', height=42)
        toolbar.pack(fill='x')
        toolbar.pack_propagate(False)

        # منوها
        menus = [
            ("فایل", self.menu_file),
            ("ویرایش", self.menu_edit),
            ("نمایش", self.menu_view),
            ("ابزارها", self.menu_tools),
            ("راهنما", self.menu_help)
        ]

        for menu_name, command in menus:
            menu_btn = tk.Button(toolbar,
                                 text=menu_name,
                                 bg='white',
                                 fg='black',
                                 bd=0,
                                 font=self.fonts['normal'],
                                 padx=15,
                                 cursor='hand2',
                                 command=command)
            menu_btn.pack(side='left')

            # افکت hover
            menu_btn.bind("<Enter>", lambda e, b=menu_btn: b.config(bg=self.colors['hover_bg']))
            menu_btn.bind("<Leave>", lambda e, b=menu_btn: b.config(bg='white'))

        # جستجو
        search_frame = tk.Frame(toolbar, bg=self.colors['hover_bg'])
        search_frame.pack(side='right', padx=10)

        search_icon = tk.Label(search_frame, text="",
                               font=("Segoe MDL2 Assets", 12),
                               bg=self.colors['hover_bg'],
                               padx=5)
        search_icon.pack(side='left')

        search_entry = tk.Entry(search_frame,
                                bd=0,
                                bg=self.colors['hover_bg'],
                                width=20,
                                font=self.fonts['normal'])
        search_entry.pack(side='left', padx=5)
        search_entry.insert(0, "جستجو...")

        # افکت focus
        search_entry.bind("<FocusIn>",
                          lambda e: search_entry.delete(0, 'end') if search_entry.get() == "جستجو..." else None)
        search_entry.bind("<FocusOut>",
                          lambda e: search_entry.insert(0, "جستجو...") if not search_entry.get() else None)

    def create_sidebar(self, parent):
        """ایجاد نوار کناری"""
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=220)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # عنوان سایدبار
        sidebar_title = tk.Label(sidebar,
                                 text="ناوبری",
                                 bg=self.colors['sidebar'],
                                 fg=self.colors['text_secondary'],
                                 font=self.fonts['subtitle'],
                                 pady=15)
        sidebar_title.pack()

        # آیتم‌های ناوبری
        nav_items = [
            ("", "صفحه اصلی", self.show_home),
            ("", "اکتشاف", self.show_explore),
            ("", "تنظیمات", self.show_settings),
            ("", "ذخیره‌ها", self.show_saves),
            ("", "دانلودها", self.show_downloads),
            ("", "سابقه", self.show_history),
            ("", "پوشه‌ها", self.show_folders),
            ("", "دستگاه‌ها", self.show_devices)
        ]

        for icon, text, command in nav_items:
            nav_btn = self.create_nav_button(sidebar, icon, text, command)
            nav_btn.pack(fill='x', padx=10, pady=2)

        # جداکننده
        separator = tk.Frame(sidebar, height=1, bg=self.colors['card_border'])
        separator.pack(fill='x', pady=20)

        # بخش سریع
        quick_title = tk.Label(sidebar,
                               text="دسترسی سریع",
                               bg=self.colors['sidebar'],
                               fg=self.colors['text_secondary'],
                               font=self.fonts['subtitle'],
                               pady=10)
        quick_title.pack()

        quick_items = [
            ("", "دسکتاپ", self.show_desktop),
            ("", "اسناد", self.show_documents),
            ("", "تصاویر", self.show_pictures),
            ("", "موسیقی", self.show_music)
        ]

        for icon, text, command in quick_items:
            quick_btn = self.create_nav_button(sidebar, icon, text, command)
            quick_btn.pack(fill='x', padx=10, pady=2)

    def create_nav_button(self, parent, icon, text, command):
        """ایجاد دکمه ناوبری"""
        btn_frame = tk.Frame(parent, bg=self.colors['sidebar'], cursor='hand2')

        # آیکون
        icon_label = tk.Label(btn_frame,
                              text=icon,
                              font=("Segoe MDL2 Assets", 14),
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_secondary'],
                              padx=10)
        icon_label.pack(side='left')

        # متن
        text_label = tk.Label(btn_frame,
                              text=text,
                              font=self.fonts['normal'],
                              bg=self.colors['sidebar'],
                              fg=self.colors['text_primary'],
                              padx=10)
        text_label.pack(side='left', fill='x', expand=True, anchor='w')

        # افکت hover
        def on_enter(e):
            btn_frame.config(bg=self.colors['hover_bg'])
            icon_label.config(bg=self.colors['hover_bg'])
            text_label.config(bg=self.colors['hover_bg'])

        def on_leave(e):
            btn_frame.config(bg=self.colors['sidebar'])
            icon_label.config(bg=self.colors['sidebar'])
            text_label.config(bg=self.colors['sidebar'])

        def on_click(e):
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

        return btn_frame

    def create_content_area(self, parent):
        """ایجاد محتوای اصلی"""
        content = tk.Frame(parent, bg=self.colors['bg'])
        content.pack(side='left', fill='both', expand=True, padx=20, pady=20)

        # هدر محتوا
        header_frame = tk.Frame(content, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=(0, 20))

        title = tk.Label(header_frame,
                         text="داشبورد اصلی",
                         font=self.fonts['title'],
                         bg=self.colors['bg'],
                         fg=self.colors['text_primary'])
        title.pack(side='left')

        date_label = tk.Label(header_frame,
                              text=datetime.now().strftime("%A, %d %B %Y"),
                              font=self.fonts['small'],
                              bg=self.colors['bg'],
                              fg=self.colors['text_secondary'])
        date_label.pack(side='right')

        # کارت‌ها
        cards_frame = tk.Frame(content, bg=self.colors['bg'])
        cards_frame.pack(fill='x', pady=10)

        # ردیف اول کارت‌ها
        row1_frame = tk.Frame(cards_frame, bg=self.colors['bg'])
        row1_frame.pack(fill='x', pady=(0, 15))

        cards_row1 = [
            ("", "ذخیره‌سازی", "۱۲۳.۴۵ GB از ۲۵۶ GB", "49%", "#0078d4"),
            ("", "پردازنده", "استفاده: ۲۴٪", "سرعت: ۳.۶ GHz", "#28a745"),
            ("", "حافظه", "۸.۲ GB از ۱۶ GB", "51%", "#17a2b8"),
            ("", "شبکه", "دانلود: ۱۲ Mbps", "آپلود: ۶ Mbps", "#6f42c1")
        ]

        for i, (icon, title_text, subtitle, info, color) in enumerate(cards_row1):
            card = self.create_card(row1_frame, icon, title_text, subtitle, info, color)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            row1_frame.columnconfigure(i, weight=1)

        # ردیف دوم کارت‌ها
        row2_frame = tk.Frame(cards_frame, bg=self.colors['bg'])
        row2_frame.pack(fill='x', pady=10)

        cards_row2 = [
            ("", "تنظیمات سیستم", "بررسی تنظیمات", "3 نیاز توجه", "#fd7e14"),
            ("", "امنیت", "ویروس‌یاب فعال", "آخرین بررسی: امروز", "#dc3545"),
            ("", "بروزرسانی‌ها", "بروزرسانی موجود", "نسخه ۲۳H۲", "#20c997"),
            ("", "پشتیبان‌گیری", "آخرین پشتیبان: ۲ روز قبل", "توصیه می‌شود", "#6c757d")
        ]

        for i, (icon, title_text, subtitle, info, color) in enumerate(cards_row2):
            card = self.create_card(row2_frame, icon, title_text, subtitle, info, color)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            row2_frame.columnconfigure(i, weight=1)

        # دکمه‌های عمل
        buttons_frame = tk.Frame(content, bg=self.colors['bg'])
        buttons_frame.pack(fill='x', pady=30)

        action_buttons = [
            ("", "شروع اسکن", self.start_scan, self.colors['button_success']),
            ("", "تنظیمات پیشرفته", self.open_settings, self.colors['button_primary']),
            ("", "پشتیبان‌گیری", self.backup_now, self.colors['button_secondary']),
            ("", "به‌روزرسانی", self.check_updates, self.colors['button_primary']),
            ("", "راه‌اندازی مجدد", self.restart_system, self.colors['button_danger'])
        ]

        for icon, text, command, color in action_buttons:
            btn = self.create_action_button(buttons_frame, icon, text, command, color)
            btn.pack(side='left', padx=5)

    def create_card(self, parent, icon, title_text, subtitle, info, color):
        """ایجاد کارت ویندوزی"""
        card = tk.Frame(parent,
                        bg=self.colors['card_bg'],
                        highlightbackground=self.colors['card_border'],
                        highlightthickness=1,
                        relief='solid')

        # هدر کارت
        header_frame = tk.Frame(card, bg=color)
        header_frame.pack(fill='x')

        icon_label = tk.Label(header_frame,
                              text=icon,
                              font=("Segoe MDL2 Assets", 16),
                              bg=color,
                              fg='white',
                              padx=10,
                              pady=5)
        icon_label.pack(side='left')

        title_label = tk.Label(header_frame,
                               text=title_text,
                               font=self.fonts['subtitle'],
                               bg=color,
                               fg='white',
                               padx=5,
                               pady=5)
        title_label.pack(side='left', fill='x', expand=True)

        # محتوای کارت
        content_frame = tk.Frame(card, bg=self.colors['card_bg'], padx=15, pady=15)
        content_frame.pack(fill='both', expand=True)

        subtitle_label = tk.Label(content_frame,
                                  text=subtitle,
                                  font=self.fonts['normal'],
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text_primary'])
        subtitle_label.pack(anchor='w', pady=(0, 5))

        info_label = tk.Label(content_frame,
                              text=info,
                              font=self.fonts['small'],
                              bg=self.colors['card_bg'],
                              fg=self.colors['text_secondary'])
        info_label.pack(anchor='w')

        # دکمه جزئیات
        detail_btn = tk.Button(content_frame,
                               text="جزئیات",
                               bg=self.colors['card_bg'],
                               fg=color,
                               bd=1,
                               relief='solid',
                               font=self.fonts['small'],
                               cursor='hand2',
                               command=lambda t=title_text: print(f"جزئیات {t}"))
        detail_btn.pack(anchor='e', pady=(10, 0))

        # افکت hover
        card.bind("<Enter>", lambda e, c=card: c.config(highlightbackground=self.colors['accent']))
        card.bind("<Leave>", lambda e, c=card: c.config(highlightbackground=self.colors['card_border']))

        return card

    def create_action_button(self, parent, icon, text, command, color):
        """ایجاد دکمه عمل با گوشه‌های گرد"""
        btn = tk.Canvas(parent,
                        width=180,
                        height=45,
                        bg=self.colors['bg'],
                        highlightthickness=0,
                        cursor='hand2')

        # ایجاد شکل گرد
        radius = 8
        btn.create_rounded_rect = lambda x1, y1, x2, y2, r, **kwargs: btn.create_polygon(
            [x1 + r, y1, x2 - r, y1, x2, y1 + r, x2, y2 - r, x2 - r, y2, x1 + r, y2, x1, y2 - r, x1, y1 + r],
            smooth=True, **kwargs
        )

        # دکمه اصلی
        button_id = btn.create_rounded_rect(2, 2, 178, 43, radius, fill=color, outline='')

        # آیکون
        icon_id = btn.create_text(30, 22,
                                  text=icon,
                                  font=("Segoe MDL2 Assets", 14),
                                  fill='white')

        # متن
        text_id = btn.create_text(100, 22,
                                  text=text,
                                  font=self.fonts['normal'],
                                  fill='white')

        # رویدادها
        def on_click(e):
            command()

        def on_enter(e):
            darker_color = self.darken_color(color, 0.9)
            btn.itemconfig(button_id, fill=darker_color)

        def on_leave(e):
            btn.itemconfig(button_id, fill=color)

        btn.bind("<Button-1>", on_click)
        btn.tag_bind(button_id, "<Button-1>", on_click)
        btn.tag_bind(icon_id, "<Button-1>", on_click)
        btn.tag_bind(text_id, "<Button-1>", on_click)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

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

        # جداکننده
        separator = tk.Label(right_frame,
                             text="|",
                             bg=self.colors['title_bar_light'],
                             fg=self.colors['text_light'],
                             font=self.fonts['small'],
                             padx=10)
        separator.pack(side='right')

        # آیکون‌های سیستم
        system_icons = ["", "", "", ""]
        for icon in system_icons:
            icon_label = tk.Label(right_frame,
                                  text=icon,
                                  bg=self.colors['title_bar_light'],
                                  fg=self.colors['text_light'],
                                  font=("Segoe MDL2 Assets", 10),
                                  padx=5,
                                  cursor='hand2')
            icon_label.pack(side='right')

    def update_time(self):
        """به‌روزرسانی زمان"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def darken_color(self, hex_color, factor=0.9):
        """تیره کردن رنگ"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        darker = tuple(int(c * factor) for c in rgb)
        return f'#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}'

    def toggle_maximize(self):
        """تغییر حالت فول اسکرین"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

    def bind_events(self):
        """اتصال رویدادها"""
        # Drag پنجره
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<ButtonRelease-1>', self.stop_move)
        self.title_bar.bind('<B1-Motion>', self.do_move)

        # کلیدهای میانبر
        self.root.bind('<F11>', lambda e: self.toggle_maximize())
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.root.bind('<Control-s>', lambda e: self.save_action())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Alt-F4>', lambda e: self.root.quit())

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        if not self.root.attributes('-fullscreen'):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def exit_fullscreen(self):
        """خروج از حالت فول اسکرین"""
        self.root.attributes('-fullscreen', False)
        self.is_fullscreen = False

    # توابع منوها
    def menu_file(self):
        print("منوی فایل باز شد")

    def menu_edit(self):
        print("منوی ویرایش باز شد")

    def menu_view(self):
        print("منوی نمایش باز شد")

    def menu_tools(self):
        print("منوی ابزارها باز شد")

    def menu_help(self):
        print("منوی راهنما باز شد")

    # توابع ناوبری
    def show_home(self):
        self.status_label.config(text="صفحه اصلی")
        print("نمایش صفحه اصلی")

    def show_explore(self):
        self.status_label.config(text="اکتشاف")
        print("نمایش اکتشاف")

    def show_settings(self):
        self.status_label.config(text="تنظیمات")
        print("نمایش تنظیمات")

    def show_saves(self):
        self.status_label.config(text="ذخیره‌ها")
        print("نمایش ذخیره‌ها")

    def show_downloads(self):
        self.status_label.config(text="دانلودها")
        print("نمایش دانلودها")

    def show_history(self):
        self.status_label.config(text="سابقه")
        print("نمایش سابقه")

    def show_folders(self):
        self.status_label.config(text="پوشه‌ها")
        print("نمایش پوشه‌ها")

    def show_devices(self):
        self.status_label.config(text="دستگاه‌ها")
        print("نمایش دستگاه‌ها")

    def show_desktop(self):
        self.status_label.config(text="دسکتاپ")
        print("نمایش دسکتاپ")

    def show_documents(self):
        self.status_label.config(text="اسناد")
        print("نمایش اسناد")

    def show_pictures(self):
        self.status_label.config(text="تصاویر")
        print("نمایش تصاویر")

    def show_music(self):
        self.status_label.config(text="موسیقی")
        print("نمایش موسیقی")

    # توابع دکمه‌های عمل
    def start_scan(self):
        self.status_label.config(text="در حال اسکن...")
        print("اسکن سیستم شروع شد")

    def open_settings(self):
        self.status_label.config(text="باز کردن تنظیمات پیشرفته")
        print("تنظیمات پیشرفته باز شد")

    def backup_now(self):
        self.status_label.config(text="در حال پشتیبان‌گیری...")
        print("پشتیبان‌گیری شروع شد")

    def check_updates(self):
        self.status_label.config(text="در حال بررسی بروزرسانی‌ها...")
        print("بررسی بروزرسانی‌ها")

    def restart_system(self):
        self.status_label.config(text="راه‌اندازی مجدد سیستم...")
        print("راه‌اندازی مجدد سیستم")

    def save_action(self):
        self.status_label.config(text="در حال ذخیره...")
        print("ذخیره انجام شد")

    def run(self):
        """اجرای برنامه"""
        self.root.mainloop()


# اجرای برنامه
if __name__ == "__main__":
    app = WindowsStyleApp()
    app.run()