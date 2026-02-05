# ui/widgets/forms.py
"""
ویجت‌های فرم ورودی سفارشی
"""
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from config.colors import APP_COLORS
from config.constants import FABRIC_COLORS, FABRIC_TYPES, SIZES, QUALITIES
from config.fonts import setup_fonts


class StyledEntry(tk.Entry):
    """ورودی متنی با استایل"""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault('font', setup_fonts()['normal'])
        kwargs.setdefault('highlightbackground', APP_COLORS['border'])
        kwargs.setdefault('highlightthickness', 1)
        kwargs.setdefault('highlightcolor', APP_COLORS['info'])
        kwargs.setdefault('relief', tk.SOLID)
        kwargs.setdefault('bd', 0)
        super().__init__(parent, **kwargs)


class StyledCombobox(ttk.Combobox):
    """کامبوباکس با استایل"""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault('font', setup_fonts()['normal'])
        kwargs.setdefault('state', 'readonly')
        super().__init__(parent, **kwargs)


class StyledSpinbox(tk.Spinbox):
    """اسپین‌باکس با استایل"""

    def __init__(self, parent, **kwargs):
        kwargs.setdefault('font', setup_fonts()['normal'])
        kwargs.setdefault('highlightbackground', APP_COLORS['border'])
        kwargs.setdefault('highlightthickness', 1)
        kwargs.setdefault('highlightcolor', APP_COLORS['info'])
        kwargs.setdefault('relief', tk.SOLID)
        kwargs.setdefault('bd', 0)
        super().__init__(parent, **kwargs)


class FormField:
    """فیلد فرم"""

    def __init__(self, parent, label_text, row, column=0,
                 sticky='w', pady=15, padx=5):
        """
        ایجاد فیلد فرم

        Args:
            parent: والد ویجت
            label_text: متن برچسب
            row: ردیف در گرید
            column: ستون در گرید
            sticky: موقعیت
            pady: فاصله عمودی
            padx: فاصله افقی
        """
        self.parent = parent
        self.row = row
        self.column = column
        self.label_text = label_text
        self.sticky = sticky
        self.pady = pady
        self.padx = padx

        # برچسب
        self.label = tk.Label(parent, text=label_text,
                              font=setup_fonts()['normal'],
                              bg=APP_COLORS['content_bg'])

        # ویجت ورودی
        self.widget = None

    def place_label(self):
        """قرار دادن برچسب"""
        self.label.grid(row=self.row, column=self.column,
                        sticky=self.sticky, pady=self.pady,
                        padx=self.padx)

    def place_widget(self, column=1):
        """قرار دادن ویجت"""
        if self.widget:
            self.widget.grid(row=self.row, column=column,
                             sticky='w', pady=self.pady,
                             padx=self.padx)

    def get_value(self):
        """دریافت مقدار"""
        if isinstance(self.widget, tk.Entry):
            return self.widget.get()
        elif isinstance(self.widget, ttk.Combobox):
            return self.widget.get()
        elif isinstance(self.widget, tk.Spinbox):
            return self.widget.get()
        elif isinstance(self.widget, tk.Text):
            return self.widget.get("1.0", tk.END).strip()
        elif isinstance(self.widget, DateEntry):
            return self.widget.get()
        return ""

    def set_value(self, value):
        """تنظیم مقدار"""
        if isinstance(self.widget, (tk.Entry, ttk.Combobox, tk.Spinbox, DateEntry)):
            if hasattr(self.widget, 'delete') and hasattr(self.widget, 'insert'):
                self.widget.delete(0, tk.END)
                self.widget.insert(0, str(value))
        elif isinstance(self.widget, tk.Text):
            self.widget.delete("1.0", tk.END)
            self.widget.insert("1.0", str(value))

    def clear(self):
        """پاک کردن مقدار"""
        self.set_value("")


class TextFormField(FormField):
    """فیلد متنی"""

    def __init__(self, parent, label_text, row, width=30, **kwargs):
        super().__init__(parent, label_text, row, **kwargs)
        self.widget = StyledEntry(parent, width=width)


class ComboFormField(FormField):
    """فیلد انتخاب از لیست"""

    def __init__(self, parent, label_text, row, values, width=30, **kwargs):
        super().__init__(parent, label_text, row, **kwargs)
        self.widget = StyledCombobox(parent, values=values, width=width)


class SpinFormField(FormField):
    """فیلد عددی"""

    def __init__(self, parent, label_text, row, from_=1, to=1000,
                 width=28, **kwargs):
        super().__init__(parent, label_text, row, **kwargs)
        self.widget = StyledSpinbox(parent, from_=from_, to=to, width=width)


class DateFormField(FormField):
    """فیلد تاریخ"""

    def __init__(self, parent, label_text, row, width=30, **kwargs):
        super().__init__(parent, label_text, row, **kwargs)
        self.widget = DateEntry(parent, font=setup_fonts()['normal'],
                                width=width, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='yyyy-mm-dd')


class TextAreaFormField(FormField):
    """فیلد متن چندخطی"""

    def __init__(self, parent, label_text, row, width=30, height=4, **kwargs):
        super().__init__(parent, label_text, row, **kwargs)
        self.widget = tk.Text(parent, font=setup_fonts()['normal'],
                              width=width, height=height,
                              highlightbackground=APP_COLORS['border'],
                              highlightthickness=1, relief=tk.SOLID, bd=0)


class GarmentEntryForm:
    """فرم ورودی پوشاک"""

    def __init__(self, parent):
        self.parent = parent
        self.fields = {}
        self.create_form()

    def create_form(self):
        """ایجاد فرم"""
        # نام محصول
        self.fields['product_name'] = TextFormField(
            self.parent, "نام محصول:", 0
        )

        # کد محصول
        self.fields['product_code'] = TextFormField(
            self.parent, "کد محصول:", 1
        )

        # سایز
        self.fields['size'] = ComboFormField(
            self.parent, "سایز:", 2, SIZES, width=15
        )

        # رنگ
        self.fields['color'] = ComboFormField(
            self.parent, "رنگ:", 3, FABRIC_COLORS, width=15
        )

        # رنگ سفارشی
        self.fields['custom_color'] = TextFormField(
            self.parent, "رنگ سفارشی:", 4, width=15
        )

        # نوع پارچه
        self.fields['fabric_type'] = ComboFormField(
            self.parent, "نوع پارچه:", 5, FABRIC_TYPES
        )

        # تاریخ ورود
        self.fields['entry_date'] = DateFormField(
            self.parent, "تاریخ ورود:", 6
        )

        # نام دوزنده
        self.fields['tailor_name'] = TextFormField(
            self.parent, "نام دوزنده:", 7
        )

        # تعداد
        self.fields['quantity'] = SpinFormField(
            self.parent, "تعداد:", 8
        )

        # توضیحات
        self.fields['notes'] = TextAreaFormField(
            self.parent, "توضیحات:", 9
        )

        # قرار دادن همه ویجت‌ها
        for field in self.fields.values():
            field.place_label()
            field.place_widget()

        # تنظیم مقادیر پیش‌فرض
        from datetime import datetime
        self.fields['size'].set_value("تک سایز")
        self.fields['quantity'].set_value("1")

    def get_data(self):
        """دریافت داده‌های فرم"""
        data = {}
        for name, field in self.fields.items():
            data[name] = field.get_value().strip()
        return data

    def set_data(self, data):
        """تنظیم داده‌های فرم"""
        for name, value in data.items():
            if name in self.fields:
                self.fields[name].set_value(value)

    def clear(self):
        """پاک کردن فرم"""
        for field in self.fields.values():
            field.clear()
        # تنظیم مجدد مقادیر پیش‌فرض
        self.fields['size'].set_value("تک سایز")
        self.fields['quantity'].set_value("1")

    def validate(self):
        """اعتبارسنجی فرم"""
        errors = []

        # بررسی فیلدهای اجباری
        required_fields = ['product_name', 'product_code', 'color',
                           'fabric_type', 'tailor_name']

        for field_name in required_fields:
            value = self.fields[field_name].get_value()
            if not value:
                errors.append(f"{self.fields[field_name].label_text} الزامی است")

        # بررسی تعداد
        try:
            quantity = int(self.fields['quantity'].get_value())
            if quantity <= 0:
                errors.append("تعداد باید بزرگتر از صفر باشد")
        except ValueError:
            errors.append("تعداد باید عدد باشد")

        return errors