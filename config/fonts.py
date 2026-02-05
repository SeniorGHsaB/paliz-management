# config/fonts.py
"""
تنظیمات فونت‌های برنامه
"""
import tkinter.font as font

def setup_fonts():
    """تنظیم و بازگرداندن دیکشنری فونت‌ها"""
    fonts = {
        'title': font.Font(family="Segoe UI", size=18, weight="bold"),
        'subtitle': font.Font(family="Segoe UI", size=14, weight="bold"),
        'normal': font.Font(family="Segoe UI", size=11),
        'small': font.Font(family="Segoe UI", size=9),
        'large': font.Font(family="Segoe UI", size=16),
        'bold': font.Font(family="Segoe UI", size=11, weight="bold")
    }
    return fonts