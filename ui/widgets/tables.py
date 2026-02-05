# ui/widgets/tables.py
"""
ویجت‌های جدول سفارشی
"""
import tkinter as tk
from tkinter import ttk
from config.colors import APP_COLORS


class CustomTreeview(ttk.Treeview):
    """جدول سفارشی با قابلیت‌های پیشرفته"""

    def __init__(self, parent, columns, **kwargs):
        """
        ایجاد جدول سفارشی

        Args:
            parent: والد ویجت
            columns: لیست ستون‌ها
            **kwargs: پارامترهای اضافی برای Treeview
        """
        super().__init__(parent, columns=columns, **kwargs)
        self.setup_style()
        self.bind_events()

    def setup_style(self):
        """تنظیم استایل جدول"""
        style = ttk.Style()
        style.theme_use('clam')

        # استایل اصلی
        style.configure("Custom.Treeview",
                        background=APP_COLORS['row_odd'],
                        foreground=APP_COLORS['text_dark'],
                        rowheight=35,
                        fieldbackground=APP_COLORS['row_odd'],
                        borderwidth=0
                        )

        # استایل هدر
        style.configure("Custom.Treeview.Heading",
                        background=APP_COLORS['sidebar'],
                        foreground=APP_COLORS['text_light'],
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat',
                        borderwidth=0
                        )

        # هایلایت انتخاب
        style.map('Custom.Treeview',
                  background=[('selected', APP_COLORS['sidebar_active'])],
                  foreground=[('selected', 'white')]
                  )

        # اعمال استایل
        self.configure(style="Custom.Treeview")

    def bind_events(self):
        """اتصال رویدادها"""
        self.bind('<Double-1>', self.on_double_click)
        self.bind('<Button-3>', self.show_context_menu)

    def on_double_click(self, event):
        """رویداد دابل کلیک"""
        region = self.identify("region", event.x, event.y)
        if region == "cell":
            item = self.identify_row(event.y)
            if item:
                self.event_generate('<<TreeviewDoubleClick>>')

    def show_context_menu(self, event):
        """نمایش منوی راست کلیک"""
        region = self.identify("region", event.x, event.y)
        if region == "cell":
            item = self.identify_row(event.y)
            if item:
                self.selection_set(item)
                self.event_generate('<<TreeviewRightClick>>')

    def setup_columns(self, column_config):
        """
        تنظیم ستون‌های جدول

        Args:
            column_config: دیکشنری {نام_ستون: (عنوان, عرض, تراز)}
        """
        for col, (heading, width, anchor) in column_config.items():
            self.heading(col, text=heading)
            self.column(col, width=width, anchor=anchor)

    def clear(self):
        """پاک کردن تمام داده‌های جدول"""
        for item in self.get_children():
            self.delete(item)

    def add_row(self, values, tags=None):
        """
        افزودن ردیف جدید

        Args:
            values: مقادیر ردیف
            tags: تگ‌های ردیف
        """
        if tags is None:
            tags = ()
        return self.insert('', 'end', values=values, tags=tags)

    def get_selected_data(self):
        """دریافت داده‌های ردیف انتخاب شده"""
        selection = self.selection()
        if selection:
            return self.item(selection[0])['values']
        return None


class SearchableTable(ttk.Frame):
    """جدول با قابلیت جستجو"""

    def __init__(self, parent, columns, column_config, height=15, **kwargs):
        """
        ایجاد جدول قابل جستجو

        Args:
            parent: والد ویجت
            columns: لیست ستون‌ها
            column_config: تنظیمات ستون‌ها
            height: ارتفاع جدول
            **kwargs: پارامترهای اضافی
        """
        super().__init__(parent, **kwargs)

        # نوار ابزار جستجو
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(fill='x', pady=(0, 5))

        # برچسب جستجو
        ttk.Label(self.toolbar, text="جستجو:").pack(side='left', padx=(0, 5))

        # فیلد جستجو
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.toolbar, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='left', padx=5)

        # دکمه پاک کردن جستجو
        self.clear_btn = ttk.Button(self.toolbar, text="✕", width=2,
                                    command=self.clear_search)
        self.clear_btn.pack(side='left', padx=2)

        # فریم جدول
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True)

        # ایجاد Treeview
        self.tree = CustomTreeview(table_frame, columns=columns,
                                   height=height, show='headings')
        self.tree.setup_columns(column_config)

        # نوار اسکرول
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical',
                                    command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal',
                                    command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set,
                            xscrollcommand=h_scrollbar.set)

        # قرار دادن ویجت‌ها
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # اتصال رویداد جستجو
        self.search_var.trace('w', self.on_search_changed)

        # داده‌های اصلی و فیلتر شده
        self.all_data = []
        self.filtered_data = []

    def on_search_changed(self, *args):
        """هنگام تغییر متن جستجو"""
        search_term = self.search_var.get().lower()
        self.filter_data(search_term)

    def filter_data(self, search_term):
        """فیلتر کردن داده‌های جدول"""
        if not search_term:
            # نمایش همه داده‌ها
            self.filtered_data = self.all_data.copy()
        else:
            # فیلتر داده‌ها
            self.filtered_data = []
            for row in self.all_data:
                if any(search_term in str(value).lower() for value in row):
                    self.filtered_data.append(row)

        self.refresh_table()

    def clear_search(self):
        """پاک کردن فیلد جستجو"""
        self.search_var.set("")

    def refresh_table(self):
        """به‌روزرسانی جدول"""
        self.tree.clear()

        for i, row in enumerate(self.filtered_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.add_row(row, tags=(tag,))

    def load_data(self, data):
        """
        بارگذاری داده در جدول

        Args:
            data: لیست داده‌ها
        """
        self.all_data = data
        self.filtered_data = data.copy()
        self.refresh_table()

    def add_data(self, row_data):
        """
        افزودن داده جدید

        Args:
            row_data: داده ردیف جدید
        """
        self.all_data.append(row_data)
        self.filtered_data.append(row_data)

        # بررسی تطابق با جستجوی فعلی
        search_term = self.search_var.get().lower()
        if not search_term or any(search_term in str(value).lower()
                                  for value in row_data):
            self.tree.add_row(row_data)

    def remove_selected(self):
        """حذف ردیف انتخاب شده"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']

            # حذف از داده‌ها
            for i, row in enumerate(self.all_data):
                if row == list(values):
                    del self.all_data[i]
                    break

            for i, row in enumerate(self.filtered_data):
                if row == list(values):
                    del self.filtered_data[i]
                    break

            # حذف از جدول
            self.tree.delete(item)

    def get_selected_row(self):
        """دریافت ردیف انتخاب شده"""
        return self.tree.get_selected_data()

    def clear_all(self):
        """پاک کردن همه داده‌ها"""
        self.all_data = []
        self.filtered_data = []
        self.tree.clear()
        self.search_var.set("")


class PaginatedTable(SearchableTable):
    """جدول با صفحه‌بندی"""

    def __init__(self, parent, columns, column_config,
                 page_size=20, height=15, **kwargs):
        """
        ایجاد جدول با صفحه‌بندی

        Args:
            parent: والد ویجت
            columns: لیست ستون‌ها
            column_config: تنظیمات ستون‌ها
            page_size: تعداد ردیف در هر صفحه
            height: ارتفاع جدول
            **kwargs: پارامترهای اضافی
        """
        super().__init__(parent, columns, column_config, height, **kwargs)

        # تنظیمات صفحه‌بندی
        self.page_size = page_size
        self.current_page = 1
        self.total_pages = 1

        # نوار صفحه‌بندی
        self.pagination_frame = ttk.Frame(self)
        self.pagination_frame.pack(fill='x', pady=(5, 0))

        # برچسب صفحه
        self.page_label = ttk.Label(self.pagination_frame, text="صفحه 1 از 1")
        self.page_label.pack(side='left', padx=5)

        # دکمه‌های صفحه‌بندی
        btn_frame = ttk.Frame(self.pagination_frame)
        btn_frame.pack(side='right')

        self.first_btn = ttk.Button(btn_frame, text="⏮", width=3,
                                    command=self.go_to_first_page)
        self.first_btn.pack(side='left', padx=1)

        self.prev_btn = ttk.Button(btn_frame, text="◀", width=3,
                                   command=self.go_to_previous_page)
        self.prev_btn.pack(side='left', padx=1)

        self.next_btn = ttk.Button(btn_frame, text="▶", width=3,
                                   command=self.go_to_next_page)
        self.next_btn.pack(side='left', padx=1)

        self.last_btn = ttk.Button(btn_frame, text="⏭", width=3,
                                   command=self.go_to_last_page)
        self.last_btn.pack(side='left', padx=1)

    def load_data(self, data):
        """بارگذاری داده با صفحه‌بندی"""
        self.all_data = data
        self.filtered_data = data.copy()
        self.current_page = 1
        self.update_pagination()
        self.refresh_table()

    def refresh_table(self):
        """به‌روزرسانی جدول با صفحه‌بندی"""
        self.tree.clear()

        # محاسبه شروع و پایان
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.filtered_data[start_idx:end_idx]

        # اضافه کردن داده‌های صفحه فعلی
        for i, row in enumerate(page_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.add_row(row, tags=(tag,))

    def update_pagination(self):
        """به‌روزرسانی اطلاعات صفحه‌بندی"""
        total_items = len(self.filtered_data)
        self.total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)

        # به‌روزرسانی برچسب
        self.page_label.config(text=f"صفحه {self.current_page} از {self.total_pages}")

        # فعال/غیرفعال کردن دکمه‌ها
        self.first_btn.state(['!disabled' if self.current_page > 1 else 'disabled'])
        self.prev_btn.state(['!disabled' if self.current_page > 1 else 'disabled'])
        self.next_btn.state(['!disabled' if self.current_page < self.total_pages else 'disabled'])
        self.last_btn.state(['!disabled' if self.current_page < self.total_pages else 'disabled'])

    def go_to_page(self, page_num):
        """رفتن به صفحه مشخص"""
        if 1 <= page_num <= self.total_pages:
            self.current_page = page_num
            self.update_pagination()
            self.refresh_table()

    def go_to_first_page(self):
        """رفتن به صفحه اول"""
        self.go_to_page(1)

    def go_to_last_page(self):
        """رفتن به صفحه آخر"""
        self.go_to_page(self.total_pages)

    def go_to_previous_page(self):
        """رفتن به صفحه قبل"""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)

    def go_to_next_page(self):
        """رفتن به صفحه بعد"""
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)

    def filter_data(self, search_term):
        """فیلتر کردن داده‌ها با صفحه‌بندی"""
        super().filter_data(search_term)
        self.current_page = 1
        self.update_pagination()