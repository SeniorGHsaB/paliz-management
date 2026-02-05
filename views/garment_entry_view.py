# views/garment_entry_view.py
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from config.colors import APP_COLORS
from config.constants import SIZES, FABRIC_COLORS, FABRIC_TYPES
from ui.widgets.tables import CustomTreeview


class GarmentEntryView:
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        """ایجاد ویجت‌های صفحه"""
        # کد مربوط به ایجاد فرم و جدول
        pass

    def get_form_data(self) -> dict:
        """دریافت داده‌های فرم"""
        pass

    def clear_form(self):
        """پاک کردن فرم"""
        pass